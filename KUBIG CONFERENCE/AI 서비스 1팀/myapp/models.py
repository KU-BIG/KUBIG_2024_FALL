from django.db import models
from django.db.models import Count, Min, Max  # 필요한 집계 함수들 임포트
from django.contrib.auth.models import AbstractUser
from django.conf import settings



class Document(models.Model):
    project_title = models.CharField(max_length=200, default='Untitled Project')
    project_description = models.TextField(default='No description provided')
    readme = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey('CustomUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='documents')
    session_key = models.CharField(max_length=100, null=True, blank=True)  # Add this field

    def __str__(self):
        return self.project_title

class SourceCode(models.Model):
    document = models.ForeignKey(
        Document, 
        on_delete=models.CASCADE,
        related_name='source_codes'
    )
    file = models.FileField(upload_to='uploads/source_code/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.document.project_title} - {self.file.name}"

class Presentation(models.Model):
    document = models.ForeignKey(
        Document, 
        on_delete=models.CASCADE,
        related_name='presentations'
    )
    file = models.FileField(upload_to='uploads/presentations/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.document.project_title} - {self.file.name}"
    
# models.py

class ButtonClick(models.Model):
    BUTTON_CHOICES = [
        ('generate_readme', 'Generate README'),
        ('copy_readme', 'Copy README'),
        ('download_files', 'Download Files'),
        ('generate_new_readme', 'Generate New README')
    ]
    
    button_name = models.CharField(max_length=50, choices=BUTTON_CHOICES)
    document = models.ForeignKey(
        Document, 
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='button_clicks'
    )
    session_id = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.button_name} - {self.session_id[:8]}"

    @classmethod
    def get_session_stats(cls):
        """세션별 사용 통계"""
        return cls.objects.values('session_id').annotate(
            click_count=Count('id'),
            first_seen=Min('created_at'),
            last_seen=Max('created_at'),
            unique_documents=Count('document', distinct=True)
        )

    @classmethod
    def get_feature_usage(cls):
        """기능별 사용 통계"""
        return cls.objects.values('button_name').annotate(
            total_clicks=Count('id'),
            unique_users=Count('session_id', distinct=True)
        )
    
# models.py에 추가
class Feedback(models.Model):
    RATING_CHOICES = [
        (1, '매우 불만족'),
        (2, '불만족'),
        (3, '보통'),
        (4, '만족'),
        (5, '매우 만족')
    ]
    
    SERVICE_TYPES = [
        ('usability', '사용성'),
        ('quality', '결과물 품질'),
        ('speed', '처리 속도'),
        ('design', '디자인/UI'),
        ('feature', '기능 제안'),
        ('other', '기타')
    ]
    
    document = models.ForeignKey(
        Document,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='feedbacks'
    )
    rating = models.IntegerField(choices=RATING_CHOICES)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES)
    content = models.TextField()
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=100)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Feedback - {self.get_service_type_display()} ({self.get_rating_display()})"
    
class CustomUser(AbstractUser):
    cookie_count = models.IntegerField(default=2)  # 초기 쿠키 2개 지급
    
    class Meta:
        db_table = 'custom_user'

class PaymentRequest(models.Model):
    PAYMENT_STATUS = [
        ('PENDING', '처리 대기'),
        ('COMPLETED', '처리 완료'),
        ('CANCELLED', '취소됨'),
    ]
    
    PAYMENT_AMOUNTS = [
        ('500', '500원 - 쿠키 1개'),
        ('1000', '1,000원 - 쿠키 3개'),
        ('5000', '5,000원 - 쿠키 20개'),
        ('10000', '10,000원 - 쿠키 50개'),
        ('50000', '50,000원 - 쿠키 300개'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payment_requests'
    )
    amount = models.CharField(
        max_length=10,
        choices=PAYMENT_AMOUNTS,
        verbose_name='결제 금액'
    )
    cookie_count = models.IntegerField(verbose_name='충전될 쿠키 수')
    transaction_date = models.DateTimeField(auto_now_add=True, verbose_name='송금 요청 일시')
    status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS,
        default='PENDING',
        verbose_name='처리 상태'
    )
    completed_date = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name='처리 완료 일시'
    )
    depositor_name = models.CharField(
        max_length=50,
        verbose_name='입금자명'
    )
    admin_note = models.TextField(
        blank=True,
        verbose_name='관리자 메모'
    )
    
    class Meta:
        verbose_name = '송금 요청'
        verbose_name_plural = '송금 요청 목록'
        ordering = ['-transaction_date']

    def __str__(self):
        return f"{self.user.username} - {self.get_amount_display()} ({self.get_status_display()})"

    def get_cookie_count_for_amount(self):
        amount_to_cookies = {
            '500': 1,
            '1000': 3,
            '5000': 20,
            '10000': 50,
            '50000': 300,
        }
        return amount_to_cookies.get(self.amount, 0)

    def save(self, *args, **kwargs):
        # 금액에 따른 쿠키 수 자동 설정
        if not self.cookie_count:
            self.cookie_count = self.get_cookie_count_for_amount()
        super().save(*args, **kwargs)

class StoreEvent(models.Model):
    EVENT_TYPES = [
        ('select_product', '상품 선택'),
        ('complete_payment', '결제 완료 클릭'),
        ('home_return', '홈으로 돌아가기'),
        ('confirm_payment', '결제 확정하기'),
        ('cancel_payment', '결제 취소')
    ]
    
    user = models.ForeignKey(
        'CustomUser', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='store_events'
    )
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    product_info = models.CharField(max_length=50, blank=True, null=True)  # 상품 선택 시 상품 정보 저장
    created_at = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=100)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = '스토어 이벤트'
        verbose_name_plural = '스토어 이벤트 목록'

    def __str__(self):
        user_str = self.user.username if self.user else 'Anonymous'
        return f"{user_str} - {self.get_event_type_display()} ({self.created_at})"