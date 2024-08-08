from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from ..forms import QuestionForm
from ..models import Question


@login_required(login_url='common:login')
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
            question.author = request.user
            question.create_date = timezone.now()
            # 실제 저장
            question.save()
            return redirect('pybo:index')
    # 질문 목록 화면에서 '질문 등록하기' 버튼 클릭 > GET 방식 요청 > 질문 등록 화면
    else:
        form = QuestionForm()
    context = {'form':form}
    return render(request, 'pybo/question_form.html', context)

@login_required(login_url='common:login')
def question_modify(request, question_id):
    '''
    pybo 질문 수정
    '''
    question = get_object_or_404(Question, pk=question_id)
    # 로그인한 사용자와 수정하려는 글쓴이가 다르면 '수정권한이 없습니다' 출력
    if request.user != question.author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('pybo:detail', question_id=question.id)
    # 질문 수정 화면에서 '저장하기' 클릭 > 데이터 수정
    if request.method == 'POST':
        # question을 기본값으로 하여 화면으로 전달받은 입력값들을 덮어써서 QuestionForm을 생성
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            question.modify_date = timezone.now()  # 수정일시 저장
            question.save()
            return redirect('pybo:detail', question_id=question.id)
    # 질문 상세 화면에서 '수정' 클릭 > GET 방식 호출 > 질문 수정 화면
    # instance=question: 기존 값을 폼에 채울 수 있다
    else:
        form = QuestionForm(instance=question)
    context = {'form': form}
    return render(request, 'pybo/question_form.html', context)

@login_required(login_url='common:login')
def question_delete(request, question_id):
    '''
    pybo 질문 삭제
    '''
    question = get_object_or_404(Question, pk=question_id)
    if request.user != question.author:
        messages.error(request, '삭제권한이 없습니다')
        return redirect('pybo:detail', question_id=question.id)
    question.delete()
    return redirect('pybo:index')