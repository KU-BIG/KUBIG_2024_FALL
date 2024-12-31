import markdown
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter  # 템플릿에서 해당 함수를 필터로 사용 가능
def sub(value, arg):
    return value - arg

''' 마크다운으로 작성한 문자열을 HTML 코드로 변환 '''
@register.filter()
def mark(value):
    # nl2br: 줄바꿈 문자를 <br> 태그로 바꿔준다 > Enter를 한 번만 눌러도 줄바꿈으로 인식
    # fenced_code: 마크다운의 소스 코드 표현
    extensions = ['nl2br', 'fenced_code']
    return mark_safe(markdown.markdown(value, extensions = extensions))