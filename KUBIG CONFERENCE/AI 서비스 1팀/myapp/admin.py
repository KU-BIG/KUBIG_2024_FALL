from django.contrib import admin
from .models import Document, SourceCode, Presentation, ButtonClick, Feedback
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from django.contrib import admin
from django.utils import timezone
from .models import PaymentRequest, StoreEvent

class SourceCodeInline(admin.TabularInline):
    model = SourceCode
    extra = 1

class PresentationInline(admin.TabularInline):
    model = Presentation
    extra = 1

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['id', 'project_title', 'created_at', 'source_code_count', 'presentation_count']
    search_fields = ['project_title', 'project_description']
    list_filter = ['created_at']
    inlines = [SourceCodeInline, PresentationInline]

    def source_code_count(self, obj):
        return obj.source_codes.count()
    source_code_count.short_description = 'Source Files'

    def presentation_count(self, obj):
        return obj.presentations.count()
    presentation_count.short_description = 'Presentation Files'

@admin.register(SourceCode)
class SourceCodeAdmin(admin.ModelAdmin):
    list_display = ['id', 'document', 'file', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['document__project_title', 'file']

@admin.register(Presentation)
class PresentationAdmin(admin.ModelAdmin):
    list_display = ['id', 'document', 'file', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['document__project_title', 'file']


@admin.register(ButtonClick)
class ButtonClickAdmin(admin.ModelAdmin):
    list_display = ('button_name', 'document', 'session_id', 'created_at')
    list_filter = ('button_name', 'created_at')
    search_fields = ('session_id', 'document__project_title')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('document')
    

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('service_type', 'rating', 'email', 'created_at', 'get_document_title')
    list_filter = ('service_type', 'rating', 'created_at')
    search_fields = ('content', 'email')
    
    def get_document_title(self, obj):
        return obj.document.project_title if obj.document else 'N/A'
    get_document_title.short_description = 'Project'

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'cookie_count', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('cookie_count',)}),
    )

admin.site.register(CustomUser, CustomUserAdmin)

@admin.register(PaymentRequest)
class PaymentRequestAdmin(admin.ModelAdmin):
    list_display = [
        'user', 
        'amount', 
        'cookie_count',
        'depositor_name',
        'transaction_date', 
        'status',
        'completed_date'
    ]
    list_filter = ['status', 'transaction_date', 'amount']
    search_fields = ['user__username', 'depositor_name', 'admin_note']
    readonly_fields = ['transaction_date']
    ordering = ['-transaction_date']
    
    actions = ['mark_as_completed', 'mark_as_cancelled']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('user', 'amount', 'cookie_count', 'depositor_name')
        }),
        ('처리 상태', {
            'fields': ('status', 'transaction_date', 'completed_date')
        }),
        ('관리자 메모', {
            'fields': ('admin_note',)
        })
    )

    @admin.action(description='선택된 요청을 처리 완료로 변경')
    def mark_as_completed(self, request, queryset):
        for payment_request in queryset.filter(status='PENDING'):
            # 상태 업데이트
            payment_request.status = 'COMPLETED'
            payment_request.completed_date = timezone.now()
            payment_request.save()
            
            # 사용자 쿠키 수 증가
            user = payment_request.user
            user.cookie_count += payment_request.cookie_count
            user.save()
            
        self.message_user(request, f"{queryset.count()}개의 요청이 처리되었습니다.")

    @admin.action(description='선택된 요청을 취소됨으로 변경')
    def mark_as_cancelled(self, request, queryset):
        queryset.update(
            status='CANCELLED',
            completed_date=timezone.now()
        )
        self.message_user(request, f"{queryset.count()}개의 요청이 취소되었습니다.")

@admin.register(StoreEvent)
class StoreEventAdmin(admin.ModelAdmin):
    list_display = ('user', 'event_type', 'product_info', 'created_at', 'session_id')
    list_filter = ('event_type', 'created_at')
    search_fields = ('user__username', 'product_info', 'session_id')
    ordering = ('-created_at',)