from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_file, name='upload_file'),
    path('', views.file_list, name='file_list'),
    path('replace/<int:file_id>/', views.replace_file, name='replace_file'),
    path('send_report/', views.send_report, name='send_report'),
    path('delete/<int:file_id>/', views.delete_file, name='delete_file'),
] 