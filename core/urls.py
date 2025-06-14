from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import FileViewSet

# Создаём router для DRF
router = DefaultRouter()
router.register(r'files', FileViewSet, basename='files')

# Стандартные URL-адреса
urlpatterns = [
    path('upload/', views.upload_file, name='upload_file'),
    path('', views.file_list, name='file_list'),
    path('replace/<int:file_id>/', views.replace_file, name='replace_file'),
    path('send_report/', views.send_report, name='send_report'),
    path('delete/<int:file_id>/', views.delete_file, name='delete_file'),
    path('profile/', views.profile, name='profile'),
    path('status/', views.status_page, name='status'),
    path('api/ml/', include('ml_api.urls')),
]

# Добавляем URL-адреса DRF
urlpatterns += router.urls 