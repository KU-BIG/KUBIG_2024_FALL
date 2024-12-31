from django.contrib import admin
from .models import Question

# 장고 Admin에 데이터 검색 기능 추가
class QuestionAdmin(admin.ModelAdmin):
    search_fields = ['subject']

admin.site.register(Question, QuestionAdmin)
