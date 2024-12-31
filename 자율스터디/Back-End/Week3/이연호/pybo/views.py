from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Question
from django.utils import timezone
from .forms import QuestionForm, AnswerForm
from django.core.paginator import Paginator

def index(request):
    """
    pybo 목록 출력
    """
    # 입력 인자
    page = request.GET.get('page', '1') # page 기본값을 1으로 지정
    # 조회
    question_list = Question.objects.order_by('-create_date') # create_date 역순으로
    # 페이징 처리
    paginator = Paginator(question_list, 10) # 페이지 당 10개씩
    page_obj = paginator.get_page(page)
    context = {'question_list': page_obj}
    return render(request, 'pybo/question_list.html', context)

def detail(request, question_id):
    """
    pybo 내용 출력
    """
    question = get_object_or_404(Question, pk=question_id) # question.id 값이 데베에 없으면 404
    context = {'question': question}
    return render(request, 'pybo/question_detail.html', context)

def answer_create(request, question_id):
    """
    pybo 답변 등록
    """
    question = get_object_or_404(Question, pk=question_id) # question.id값이 데베에 없으면 404
    if request.method == "POST": # create의 method
        form = AnswerForm(request.POST) # 화면에서 전달받은 데이터로 content값 채움
        if form.is_valid(): # form이 유효하면
            answer = form.save(commit=False) # 임시 저장
            answer.create_date = timezone.now()
            answer.question = question
            answer.save() # 실제 저장
            return redirect('pybo:detail', question_id=question.id) # type: ignore
    else:
        form = AnswerForm() # content 받아옴
    context = {'question':question, 'form':form} # question, content
    return render(request, 'pybo/question_detail.html', context)

def question_create(request):
    """
    pybo 질문 등록
    """
    if request.method == 'POST': # create의 method
        form = QuestionForm(request.POST) # 화면에서 전달받은 데이터로 subject, content값 채움
        if form.is_valid(): # form이 유효하면
            question = form.save(commit=False) # 임시 저장
            question.create_date = timezone.now()
            question.save() # 실제 저장
            return redirect('pybo:index')
    else:
        form = QuestionForm() # subject, content 받아옴
    context = {'form': form} # subject, content
    return render(request, 'pybo/question_form.html', context)