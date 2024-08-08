from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Count
from ..models import Question

''' pybo 목록 출력 '''
def index(request):
    # 입력 인자
    page = request.GET.get('page', '1')  # 페이지
    kw = request.GET.get('kw', '')  # 검색어
    so = request.GET.get('so', 'recent')  # 정렬 기준

    # 정렬
    if so == 'recommend':
        # annotate: 모델에 없는, num_voter 필드를 임시로 추가
        question_list = Question.objects.annotate(
            num_voter = Count('voter')).order_by('-num_voter', '-create_date')
    elif so == 'popular':
        question_list = Question.objects.annotate(
            num_answer = Count('answer')).order_by('-num_answer', '-create_date')
    else:  # recent
        question_list = Question.objects.order_by('-create_date')

    # 조회
    if kw:
        question_list = question_list.filter(
            # __icontains: 대소문자를 가리지 않고, 필드에 문자열이 포함되었는지 찾아줌
            Q(subject__icontains = kw) |  # 제목 검색
            Q(content__icontains = kw) |  # 내용 검색
            Q(author__username__icontains = kw) |  # 질문 글쓴이 검색
            Q(answer__author__username__icontains = kw)  # 답변 글쓴이 검색
        ).distinct()

    # 페이징 처리
    paginator = Paginator(question_list, 10)  # 페이지당 10개씩 보여주기
    page_obj = paginator.get_page(page)

    context = {'question_list': page_obj, 'page': page, 'kw': kw, 'so': so}
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