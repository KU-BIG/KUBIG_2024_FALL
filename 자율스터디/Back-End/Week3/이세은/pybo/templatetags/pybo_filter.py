from django import template

register = template.Library()

@register.filter  # 템플릿에서 해당 함수를 필터로 사용 가능
def sub(value, arg):
    return value - arg