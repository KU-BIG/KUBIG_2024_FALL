from django.db import models
from django.contrib.auth.models import User

# 질문 모델
class Question(models.Model):
    # User 모델은 django.contrib.auth 앱이 제공
    # on_delete=models.CASCADE: 계정이 삭제되면 계정과 연결된 Question 모델 데이터를 모두 삭제
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='author_question')
    # CharField: 글자 수 제한하고 싶은 데이터
    subject = models.CharField(max_length=200)
    # TextField: 글자 수 제한 없는 데이터
    content = models.TextField()
    create_date = models.DateTimeField()
    # null=True: null을 허용
    # blank=True: form.is_valid()를 통한 입력 폼 데이터 검사 시 값이 없어도 된다
    modify_date = models.DateTimeField(null=True, blank=True)
    voter = models.ManyToManyField(User,
                                   related_name='voter_question')

    def __str__(self):
        return self.subject

# 답변 모델
class Answer(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='author_answer')
    # Answer 모델은 Question 모델을 속성으로 가짐
    # on_delete = models.CASCADE: 답변에 연결된 질문이 삭제되면 답변도 함께 삭제
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    content = models.TextField()
    create_date = models.DateTimeField()
    modify_date = models.DateTimeField(null=True, blank=True)
    voter = models.ManyToManyField(User,
                                   related_name='voter_answer')


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    create_date = models.DateTimeField()
    modify_date = models.DateTimeField(null=True, blank=True)
    question = models.ForeignKey(Question, null=True, blank=True, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, null=True, blank=True, on_delete=models.CASCADE)