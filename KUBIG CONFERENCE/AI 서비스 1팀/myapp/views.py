from django.shortcuts import render, redirect
from django.core.files.base import ContentFile
from .models import Document
from .readme_generator import process_uploaded_files
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.files.base import ContentFile
from wsgiref.util import FileWrapper
import zipfile
import io
import os
from django.conf import settings
from django.urls import reverse
import threading
import logging
from .models import Document, SourceCode, Presentation, Feedback, ButtonClick
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from .models import PaymentRequest, StoreEvent
import json
from .forms import CustomLoginForm  # 새로 만든 폼 import



logger = logging.getLogger(__name__)

def home(request):
    if request.method == 'POST':
        source_codes = request.FILES.getlist('source_code')
        presentations = request.FILES.getlist('presentation')
        project_title = request.POST.get('project_title')
        project_description = request.POST.get('project_description')
        
        # Store previous data
        previous_data = {
            'project_title': project_title,
            'project_description': project_description,
        }
        
        if not all([source_codes, project_title]):
            return render(request, 'home.html', {
                'error': 'Please fill in all required fields.',
                'previous_data': previous_data
            })
            
        # 비로그인 사용자 체크
        if not request.user.is_authenticated:
            # 세션에서 readme 생성 횟수 확인
            readme_count = request.session.get('readme_count', 0)
            
            # 1회 이상 생성한 경우 로그인 페이지로 리다이렉트
            if readme_count >= 1:
                # 로그인 후 처리를 위해 next 파라미터에 현재 페이지 URL 추가
                next_url = reverse('home')
                return redirect(f'{reverse("login")}?next={next_url}')
            
            # readme_count 증가
            request.session['readme_count'] = readme_count + 1
            request.session.modified = True
            
        try:
            # Create main Document object with session_key
            document = Document.objects.create(
                project_title=project_title,
                project_description=project_description,
                user=request.user if request.user.is_authenticated else None,
                session_key=request.session.session_key
            )
            
            # Process source code files
            for source_code in source_codes:
                source_code_content = source_code.read()
                try:
                    source_code_text = source_code_content.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        source_code_text = source_code_content.decode('cp949')
                    except UnicodeDecodeError:
                        source_code_text = source_code_content.decode('euc-kr', errors='ignore')
                
                # Save source code file
                SourceCode.objects.create(
                    document=document,
                    file=ContentFile(source_code_text.encode('utf-8'), name=source_code.name)
                )
            
            # Process presentation files
            if presentations:
                for presentation in presentations:
                    Presentation.objects.create(
                        document=document,
                        file=presentation
                    )
            
            # Store document_id in session
            if not request.user.is_authenticated:
                if not request.session.get('pending_documents'):
                    request.session['pending_documents'] = []
                request.session['pending_documents'].append(document.id)
                request.session.modified = True
            
            threading.Thread(target=generate_readme, args=(document.id,)).start()
            return HttpResponseRedirect(reverse('loading') + f'?document_id={document.id}')
            
        except Exception as e:
            logger.error(f"Error processing files: {str(e)}")
            return render(request, 'home.html', {
                'error': str(e),
                'previous_data': previous_data
            })
    
    return render(request, 'home.html')

def generate_readme(document_id):
    try:
        document = Document.objects.get(id=document_id)
        readme_content = process_uploaded_files(document)
        document.readme = readme_content
        document.save()
        
        # Get the user who created this document
        if document.user:
            user = document.user
            user.cookie_count = max(0, user.cookie_count - 1)
            user.save()
            logger.info(f"Cookie deducted for user {user.username}")
        
        logger.info(f"README generated successfully for document {document_id}")
    except Exception as e:
        logger.error(f"Error generating README for document {document_id}: {str(e)}")


def regenerate_readme(request, document_id):
    try:
        document = Document.objects.get(id=document_id)
        readme_content = process_uploaded_files(document)
        document.readme = readme_content
        document.save()
        return HttpResponseRedirect(reverse('result') + f'?document_id={document_id}')
    except Document.DoesNotExist:
        return render(request, 'home.html', {'error': 'Document not found.'})
    except Exception as e:
        return render(request, 'home.html', {'error': str(e)})

def download_files(request, document_id):
    document = Document.objects.get(id=document_id)
    
    # Create ZIP file
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # Add README
        zip_file.writestr('README.md', document.readme)
        
        # Add source code files
        for source_code in document.source_codes.all():
            file_path = os.path.join(settings.MEDIA_ROOT, source_code.file.name)
            if os.path.exists(file_path):
                # Get the original file name from the uploaded file
                original_name = source_code.file.name.split('/')[-1]  # Get just the filename
                # Remove only the random string that Django adds
                if '_' in original_name:
                    name_parts = original_name.rsplit('_', 1)  # Split from the right side only once
                    if len(name_parts) == 2 and len(name_parts[1]) >= 7:  # Check if second part looks like a random string
                        original_name = name_parts[0] + os.path.splitext(name_parts[1])[1]
                zip_file.write(file_path, f'source_code/{original_name}')
        
        # Add presentation files
        for presentation in document.presentations.all():
            file_path = os.path.join(settings.MEDIA_ROOT, presentation.file.name)
            if os.path.exists(file_path):
                # Get the original file name from the uploaded file
                original_name = presentation.file.name.split('/')[-1]  # Get just the filename
                # Remove only the random string that Django adds
                if '_' in original_name:
                    name_parts = original_name.rsplit('_', 1)  # Split from the right side only once
                    if len(name_parts) == 2 and len(name_parts[1]) >= 7:  # Check if second part looks like a random string
                        original_name = name_parts[0] + os.path.splitext(name_parts[1])[1]
                zip_file.write(file_path, f'presentations/{original_name}')
    
    # Reset buffer
    zip_buffer.seek(0)
    
    # Set up HTTP response
    response = HttpResponse(FileWrapper(zip_buffer), content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="project_files_{document_id}.zip"'
    
    return response

def loading(request):
    document_id = request.GET.get('document_id')
    if document_id:
        try:
            document = Document.objects.get(id=document_id)
            return render(request, 'loading.html', {'document_id': document_id})
        except Document.DoesNotExist:
            return render(request, 'home.html', {'error': 'Document not found.'})
    return render(request, 'home.html', {'error': 'Document ID not provided.'})

def check_readme_status(request):
    document_id = request.GET.get('document_id')
    if document_id:
        try:
            document = Document.objects.get(id=document_id)
            if document.readme:
                return JsonResponse({'status': 'complete'})
            else:
                return JsonResponse({'status': 'in_progress'})
        except Document.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Document not found.'})
    return JsonResponse({'status': 'error', 'message': 'Document ID not provided.'})

def result(request):
    document_id = request.GET.get('document_id')
    if document_id:
        try:
            document = Document.objects.get(id=document_id)
            
            # 비로그인 사용자의 경우
            if not request.user.is_authenticated:
                readme_count = request.session.get('readme_count', 0)
                # 첫 번째 생성이 아닌 경우 로그인 페이지로 리다이렉트
                if readme_count > 1:
                    return redirect('login')
            # 로그인 사용자의 경우 쿠키 체크
            else:
                if request.user.cookie_count <= 0:
                    return redirect('cookie_store')
                    
            return render(request, 'result.html', {'document': document})
        except Document.DoesNotExist:
            return render(request, 'home.html', {'error': 'Document not found.'})
    return HttpResponseRedirect(reverse('home'))

@require_POST
def track_button_click(request):
    try:
        button_name = request.POST.get('button_name')
        document_id = request.POST.get('document_id')
        session_id = request.POST.get('session_id')
        
        ButtonClick.objects.create(
            button_name=button_name,
            document_id=document_id if document_id else None,
            session_id=session_id
        )
        return JsonResponse({'status': 'success'})
    except Exception as e:
        logger.error(f"Error tracking button click: {str(e)}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    

def feedback_view(request):
    context = {
        'rating_choices': Feedback.RATING_CHOICES,
        'service_types': Feedback.SERVICE_TYPES
    }
    return render(request, 'feedback.html', context)

@require_http_methods(["POST"])
def submit_feedback(request):
    try:
        feedback = Feedback.objects.create(
            document_id=request.POST.get('document_id'),
            rating=request.POST.get('rating'),
            service_type=request.POST.get('service_type'),
            content=request.POST.get('content'),
            email=request.POST.get('email') or None,
            session_id=request.session.session_key or 'anonymous'
        )
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
@method_decorator(csrf_protect, name='dispatch')
class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    redirect_authenticated_user = True
    form_class = CustomLoginForm

    def form_valid(self, form):
        response = super().form_valid(form)
        
        # After successful login, redirect to home if coming from there
        next_url = self.request.GET.get('next')
        if next_url and next_url == reverse('home'):
            # Let the user create a new document after login
            if 'readme_count' in self.request.session:
                del self.request.session['readme_count']
            self.request.session.modified = True
            return HttpResponseRedirect(next_url)
            
        # Otherwise, process any pending documents
        pending_documents = self.request.session.get('pending_documents', [])
        if pending_documents:
            # Update the user field for all pending documents
            Document.objects.filter(id__in=pending_documents).update(user=self.request.user)
            
            # Check if user has enough cookies
            if self.request.user.cookie_count <= 0:
                # Clear the pending documents list
                del self.request.session['pending_documents']
                self.request.session.modified = True
                return redirect('cookie_store')
            
            # Deduct cookie for the most recent document
            user = self.request.user
            user.cookie_count = max(0, user.cookie_count - 1)
            user.save()
            logger.info(f"Cookie deducted for user {user.username} after login")
            
            # Clear the pending documents list and readme count
            del self.request.session['pending_documents']
            if 'readme_count' in self.request.session:
                del self.request.session['readme_count']
            self.request.session.modified = True
            
            # Get the last document ID (most recent)
            last_document_id = pending_documents[-1]
            # Redirect to result page for the last document
            return HttpResponseRedirect(reverse('result') + f'?document_id={last_document_id}')
            
        return response

    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse('home')
    
def logout_view(request):
    logout(request)
    return redirect('home')

def register(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            # next 파라미터가 있으면 해당 URL로 리다이렉트
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {
        'form': form,
        'next': request.GET.get('next')  # next 파라미터를 템플릿에 전달
    })

def error_view(request):
    error_message = request.GET.get('error', '오류가 발생했습니다.')
    return render(request, 'error.html', {'error': error_message})

@login_required(login_url='login')
def cookie_store(request):
    context = {
        'user': request.user,
        'message': '쿠키가 부족합니다. 추가 쿠키를 구매해주세요.' if request.user.cookie_count <= 0 else None
    }
    return render(request, 'cookie_store.html', context)

@login_required
def submit_payment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            amount = data.get('amount')
            depositor_name = data.get('depositor_name')
            
            # 금액에서 숫자만 추출 (예: "1,000원 - 쿠키 3개" -> "1000")
            amount_value = ''.join(filter(str.isdigit, amount.split('-')[0]))
            
            # 금액별 쿠키 수량 매핑
            amount_to_cookies = {
                '500': 1,
                '1000': 3,
                '5000': 20,
                '10000': 50,
                '50000': 300,
            }
            
            # 충전될 쿠키 수 계산
            cookies_to_add = amount_to_cookies.get(amount_value, 0)
            
            # 결제 요청 생성 - status는 PENDING 유지
            payment_request = PaymentRequest.objects.create(
                user=request.user,
                amount=amount_value,
                depositor_name=depositor_name,
                cookie_count=cookies_to_add,
                status='PENDING'  # 대기 상태로 설정
            )
            
            # 사용자의 쿠키 수 즉시 증가
            user = request.user
            user.cookie_count += cookies_to_add
            user.save()
            
            return JsonResponse({
                'status': 'success',
                'message': f'쿠키 {cookies_to_add}개가 충전되었습니다.',
                'new_cookie_count': user.cookie_count
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    return JsonResponse({
        'status': 'error',
        'message': '잘못된 요청입니다.'
    }, status=400)


@require_POST
def track_store_event(request):
    try:
        data = json.loads(request.body)
        event_type = data.get('event_type')
        product_info = data.get('product_info', None)
        
        StoreEvent.objects.create(
            user=request.user if request.user.is_authenticated else None,
            event_type=event_type,
            product_info=product_info,
            session_id=request.session.session_key or 'anonymous'
        )
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)