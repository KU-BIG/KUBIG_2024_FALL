from django.urls import path
from . import views
from django.views.static import serve
import os
from .views import CustomLoginView


def serve_js(request):
    js_path = os.path.join(os.path.dirname(__file__), 'tracking.js')
    return serve(request, os.path.basename(js_path), os.path.dirname(js_path))

urlpatterns = [
    path('', views.home, name='home'),
    path('regenerate/<int:document_id>/', views.regenerate_readme, name='regenerate_readme'),
    path('download/<int:document_id>/', views.download_files, name='download_files'),
    path('loading/', views.loading, name='loading'),
    path('result/', views.result, name='result'),
    path('check_readme_status/', views.check_readme_status, name='check_readme_status'),
    path('track-click/', views.track_button_click, name='track_button_click'),
    path('myapp/tracking.js', serve_js),
    path('feedback/', views.feedback_view, name='feedback'),
    path('feedback/submit/', views.submit_feedback, name='submit_feedback'),
    path('error/', views.error_view, name='error'),
    path('store/', views.cookie_store, name='cookie_store'),
    path('submit-payment/', views.submit_payment, name='submit_payment'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('track-store-event/', views.track_store_event, name='track_store_event'),

]