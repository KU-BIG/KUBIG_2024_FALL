from django.http import HttpResponse
from .models import Question
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .forms import QuestionForm, AnswerForm
from django.core.paginator import Paginator

def index(request):
    '''
    pybo 목록 출력
    '''
    # 입력 인자
    page = request.GET.get('page', '1')

    # 조회
    question_list = Question.objects.order_by('-create_date')

    # 페이징 처리
    paginator = Paginator(question_list, 10)
    page_obj = paginator.get_page(page)

    context = {'question_list': page_obj}
    return render(request, 'pybo/question_list.html', context)

def detail(request, question_id):
    '''
    pybo 내용 출력
    '''
    # 모델의 기본키를 이용하여 모델 객체 한 건을 반환
    # 해당하는 건이 없으면 오류 대신 404 페이지 반환
    question = get_object_or_404(Question, pk=question_id)
    context = {'question': question}
    return render(request, 'pybo/question_detail.html', context)

def answer_create(request, question_id):
    '''
    pybo 답변 등록
    '''
    question = get_object_or_404(Question, pk=question_id)
    if request.method == "POST":
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.create_date = timezone.now()
            answer.question = question
            answer.save()
            # redirect(이동할 페이지의 별칭, 해당 URL에 전달해야 하는 값)
            return redirect('pybo:detail', question_id=question.id)
    else:
        form = AnswerForm()
    context = {'question': question, 'form': form}
    return render(request, 'pybo/question_detail.html', context)

def question_create(request):
    '''
    pybo 질문 등록
    '''
    # 질문 등록 화면에서 입력값 채우고 '저장하기' 버튼 클릭 > POST 방식 요청 > 데이터 저장
    if request.method == 'POST':
        # 화면에서 전달받은 데이터로 폼이 채워지도록 객체를 생성
        form = QuestionForm(request.POST)
        # form이 유효한지 검사
        if form.is_valid():
            # 임시 저장
            question = form.save(commit=False)
            question.create_date = timezone.now()
            # 실제 저장
            question.save()
            return redirect('pybo:index')
    # 질문 목록 화면에서 '질문 등록하기' 버튼 클릭 > GET 방식 요청 > 질문 등록 화면
    else:
        form = QuestionForm()
    context = {'form':form}
    return render(request, 'pybo/question_form.html', context)