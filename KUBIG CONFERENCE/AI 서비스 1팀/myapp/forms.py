from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label='이메일',
        widget=forms.EmailInput(attrs={
            'class': 'auth-input',
            'placeholder': '이메일을 입력해주세요'
        })
    )
    
    # username 필드 재정의
    username = forms.CharField(
        label='유저 이름',
        widget=forms.TextInput(attrs={
            'class': 'auth-input',
            'placeholder': '사용할 유저 이름을 입력해주세요'
        })
    )
    
    # password1 필드 재정의
    password1 = forms.CharField(
        label='비밀번호',
        widget=forms.PasswordInput(attrs={
            'class': 'auth-input',
            'placeholder': '비밀번호를 입력해주세요'
        })
    )
    
    # password2 필드 재정의
    password2 = forms.CharField(
        label='비밀번호 확인',
        widget=forms.PasswordInput(attrs={
            'class': 'auth-input',
            'placeholder': '비밀번호를 한번 더 입력해주세요'
        })
    )

    class Meta:
        model = CustomUser
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 불필요한 help_text 제거
        self.fields['username'].help_text = None
        self.fields['password1'].help_text = '8자 이상의 영문, 숫자 조합을 사용하세요.'
        self.fields['password2'].help_text = None

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
    
# forms.py

from django import forms
from django.contrib.auth.forms import AuthenticationForm

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label='유저 이름',
        widget=forms.TextInput(attrs={
            'class': 'auth-input',
            'placeholder': '유저 이름을 입력해주세요'
        })
    )
    
    password = forms.CharField(
        label='비밀번호',
        widget=forms.PasswordInput(attrs={
            'class': 'auth-input',
            'placeholder': '비밀번호를 입력해주세요'
        })
    )