from django import forms
from pybo.models import Question, Answer, Comment

# 질문 등록 폼
# 모델 폼: 모델과 연결된 폼
# 모델 폼 객체를 저장하면 연결된 모델의 데이터를 저장 가능
class QuestionForm(forms.ModelForm):
    # 모델 폼은 Meta 클래스를 반드시 가져야 함
    class Meta:
        # 모델 폼과 연결된 모델
        model = Question
        # 사용할 모델의 필드
        fields = ['subject', 'content']
        '''
        폼에 부트스트랩 적용
        widgets = {
            'subject': forms.TextInput(attrs={'class':'form-control'}),
            'content': forms.Textarea(attrs={'class':'form-control', 'rows':10}),
        }
        '''
        labels = {
            'subject': '제목',
            'content': '내용',
        }

# 답변 등록 폼
class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['content']
        labels = {
            'content': '답변내용',
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        labels = {
            'content': '댓글내용',
        }