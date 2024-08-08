from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from common.forms import UserForm

def signup(request):
    '''
    회원가입
    '''
    # POST > 화면에서 입력한 데이터로 새로운 사용자를 생성
    if request.method == 'POST':
        form = UserForm(request.POST)
        # is_valid(): 회원가입 화면의 필드값 3개가 모두 입력되었는지, 비밀번호1,2가 같은지, 비밀번호 값이 생성 규칙에 맞는지 등 검사
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('index')
    # GET > common/signup.html 화면 반환
    else:
        form = UserForm()
    return render(request, 'common/signup.html', {'form': form})

