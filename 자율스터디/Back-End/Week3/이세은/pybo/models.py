from django.db import models

# 질문 모델
class Question(models.Model):
    # CharField: 글자 수 제한하고 싶은 데이터
    subject = models.CharField(max_length=200)
    # TextField: 글자 수 제한 없는 데이터
    content = models.TextField()
    create_date = models.DateTimeField()

    def __str__(self):
        return self.subject

# 답변 모델
class Answer(models.Model):
    # Answer 모델은 Question 모델을 속성으로 가짐
    # on_delete = models.CASCADE: 답변에 연결된 질문이 삭제되면 답변도 함께 삭제
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    content = models.TextField()
    create_date = models.DateTimeField()