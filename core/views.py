from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.utils.translation import gettext_lazy as _ # Импортируем функцию перевода
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count, Max
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .forms import FileUploadForm, EmailForm # Импортируем обе формы
from .models import StoredFile # Импортируем модель StoredFile
from .serializers import FileSerializer
import os # Импортируем модуль os для работы с файлами
import logging # Импортируем модуль логирования
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

logger = logging.getLogger(__name__) # Получаем экземпляр логгера для текущего модуля

# Create your views here.

def send_file_notification(file_instance, action):
    # Get just the filename from the full path
    filename = os.path.basename(file_instance.file.name)
    subject = f'Файл {action}: {filename}'
    message = f'Файл {file_instance.file.name} был {action}.\nОписание: {file_instance.description}'
    from_email = settings.EMAIL_HOST_USER
    to_email = 'filemanagerforpp@mail.ru'
    
    try:
        email = EmailMessage(
            subject,
            message,
            from_email,
            [to_email]
        )
        
        # Проверяем существование файла перед прикреплением
        if file_instance.file and os.path.exists(file_instance.file.path):
            email.attach_file(file_instance.file.path)
        
        email.send()
        logger.info(f"Уведомление о файле '{file_instance.file.name}' ({action}) успешно отправлено.")
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления о файле '{file_instance.file.name}' ({action}): {e}")

@login_required
def upload_file(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file_instance = form.save(commit=False)
            file_instance.user = request.user
            file_instance.save()
            # Отправляем уведомление о создании файла
            send_file_notification(file_instance, 'создан')
            logger.info(f"Пользователь {request.user.username} успешно загрузил файл '{file_instance.file.name}'.")
            return redirect('file_list')
        else:
            logger.warning(f"Пользователь {request.user.username} пытался загрузить файл с ошибками формы: {form.errors}")
    else:
        form = FileUploadForm()
    return render(request, 'core/upload.html', {'form': form})

@login_required
def file_list(request):
    files = StoredFile.objects.filter(user=request.user) # Получаем все файлы из базы данных
    logger.info(f"Пользователь {request.user.username} просматривает список файлов.")
    return render(request, 'core/list.html', {'files': files})

@login_required
def replace_file(request, file_id):
    file_instance = get_object_or_404(StoredFile, id=file_id, user=request.user) # Получаем объект файла или 404 ошибку
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES, instance=file_instance)
        if form.is_valid():
            # Сохраняем информацию о старом файле
            old_file_path = None
            old_file_name = None
            if file_instance.file:
                old_file_path = file_instance.file.path
                old_file_name = file_instance.file.name

            # Сохраняем новую информацию о файле
            file_instance = form.save()

            # Удаляем старый файл после успешного сохранения нового
            if old_file_path and os.path.exists(old_file_path):
                try:
                    os.remove(old_file_path)
                    logger.info(f"Старый файл '{old_file_name}' был успешно удален после замены.")
                except Exception as e:
                    logger.error(f"Ошибка удаления старого файла '{old_file_name}' после замены: {e}")

            # Отправляем уведомление о замене файла
            notification_message = f'Файл {old_file_name} был заменен на {file_instance.file.name}.\nОписание: {file_instance.description}'
            try:
                email = EmailMessage(
                    f'Файл заменен: {old_file_name} -> {file_instance.file.name}',
                    notification_message,
                    settings.EMAIL_HOST_USER,
                    ['filemanagerforpp@mail.ru']
                )
                if file_instance.file and os.path.exists(file_instance.file.path):
                    email.attach_file(file_instance.file.path)
                email.send()
                logger.info(f"Уведомление о замене файла '{old_file_name}' на '{file_instance.file.name}' успешно отправлено.")
            except Exception as e:
                logger.error(f"Ошибка отправки уведомления о замене файла '{old_file_name}' на '{file_instance.file.name}': {e}")

            logger.info(f"Пользователь {request.user.username} успешно заменил файл '{old_file_name}' на '{file_instance.file.name}'.")
            return redirect('file_list') # Редирект на список файлов
        else:
            logger.warning(f"Пользователь {request.user.username} пытался заменить файл {file_instance.file.name} с ошибками формы: {form.errors}")
            return render(request, 'core/replace.html', {'form': form, 'file_instance': file_instance}, status=200)
    else:
        form = FileUploadForm(instance=file_instance)
    return render(request, 'core/replace.html', {'form': form, 'file_instance': file_instance})

@login_required
def send_report(request):
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            to_email = form.cleaned_data['to_email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            selected_file = form.cleaned_data['selected_file']
            from_email = settings.EMAIL_HOST_USER

            try:
                email = EmailMessage(
                    subject,
                    message,
                    from_email,
                    [to_email]
                )
                
                # Если выбран файл, прикрепляем его к письму
                if selected_file and os.path.exists(selected_file.file.path):
                    email.attach_file(selected_file.file.path)
                
                email.send()
                logger.info(f"Отчет на почту {to_email} успешно отправлен пользователем {request.user.username}.")
                return redirect('file_list')
            except Exception as e:
                logger.error(f"Ошибка отправки отчета на почту {to_email} пользователем {request.user.username}: {e}")
        else:
            logger.warning(f"Пользователь {request.user.username} пытался отправить отчет с ошибками формы: {form.errors}")
    else:
        form = EmailForm()
    return render(request, 'core/email_form.html', {'form': form})

@login_required
def delete_file(request, file_id):
    file_instance = get_object_or_404(StoredFile, id=file_id, user=request.user)
    
    # Сохраняем информацию о файле перед удалением
    file_path = None
    file_name = None
    file_description = None
    
    if file_instance.file:
        file_path = file_instance.file.path
        file_name = file_instance.file.name
        file_description = file_instance.description
    
    # Удаляем запись из базы данных
    file_instance.delete()
    
    # Удаляем файл с диска после удаления из базы данных
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
            logger.info(f"Файл '{file_name}' был успешно удален с диска.")
        except Exception as e:
            logger.error(f"Ошибка удаления файла '{file_name}' с диска: {e}")
    
    # Отправляем уведомление об удалении файла
    try:
        email = EmailMessage(
            f'Файл удален: {file_name}',
            f'Файл {file_name} был удален.\nОписание: {file_description}',
            settings.EMAIL_HOST_USER,
            ['filemanagerforpp@mail.ru']
        )
        email.send()
        logger.info(f"Уведомление об удалении файла '{file_name}' успешно отправлено.")
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления об удалении файла '{file_name}': {e}")
    
    logger.info(f"Пользователь {request.user.username} успешно удалил файл '{file_name}'.")
    return redirect('file_list')

@login_required
def profile(request):
    # Получаем статистику пользователя
    user_stats = {
        'total_files': StoredFile.objects.filter(user=request.user).count(),
        'last_activity': StoredFile.objects.filter(user=request.user).aggregate(
            last_activity=Max('uploaded_at')
        )['last_activity'],
        'recent_files': StoredFile.objects.filter(user=request.user).order_by('-uploaded_at')[:5]
    }
    logger.info(f"Пользователь {request.user.username} просматривает свой профиль.")
    return render(request, 'core/profile.html', {'user_stats': user_stats})

def status_page(request):
    total_users = User.objects.count()
    total_files_size = 0
    for stored_file in StoredFile.objects.all():
        if stored_file.file and os.path.exists(stored_file.file.path):
            total_files_size += stored_file.file.size
    
    total_files_size_mb = round(total_files_size / (1024 * 1024), 2) # Calculate this before logging

    # Простая проверка статуса email-сервиса
    email_configured = all([
        settings.EMAIL_HOST,
        settings.EMAIL_PORT,
        settings.EMAIL_HOST_USER,
        settings.EMAIL_HOST_PASSWORD
    ])
    email_status = "Настроен и доступен" if email_configured else "Не настроен или не все данные указаны"

    context = {
        'total_users': total_users,
        'total_files_size_mb': total_files_size_mb, # Use the calculated variable
        'email_status': email_status,
    }
    logger.info(f"Запрошена страница статуса. Пользователей: {total_users}, Общий размер файлов: {total_files_size_mb} MB, Статус Email: {email_status}.")
    return render(request, 'core/status.html', context)

class FileViewSet(viewsets.ModelViewSet):
    queryset = StoredFile.objects.all()
    serializer_class = FileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['description']
    search_fields = ['description']

    def get_queryset(self):
        logger.info(f"API: Пользователь {self.request.user.username} запрашивает список файлов через API.")
        # Ensure users can only see their own files
        return StoredFile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        file_instance = serializer.save(user=self.request.user)
        send_file_notification(file_instance, 'создан')
        logger.info(f"API: Пользователь {self.request.user.username} успешно загрузил файл '{file_instance.file.name}' через API.")

    def perform_update(self, serializer):
        old_file = self.get_object()
        old_file_name = old_file.file.name
        file_instance = serializer.save()
        
        # Send notification about file replacement
        notification_message = f'Файл {old_file_name} был заменен на {file_instance.file.name}.\nОписание: {file_instance.description}'
        try:
            email = EmailMessage(
                f'Файл заменен: {os.path.basename(old_file_name)} -> {os.path.basename(file_instance.file.name)}',
                notification_message,
                settings.EMAIL_HOST_USER,
                ['filemanagerforpp@mail.ru']
            )
            if file_instance.file and os.path.exists(file_instance.file.path):
                email.attach_file(file_instance.file.path)
            email.send()
            logger.info(f"API: Уведомление о замене файла '{old_file_name}' на '{file_instance.file.name}' успешно отправлено.")
        except Exception as e:
            logger.error(f"API: Ошибка отправки уведомления о замене файла '{old_file_name}' на '{file_instance.file.name}': {e}")

    def perform_destroy(self, instance):
        file_name = instance.file.name
        file_description = instance.description
        
        # Delete the file
        instance.delete()
        
        # Send notification about file deletion
        try:
            email = EmailMessage(
                f'Файл удален: {os.path.basename(file_name)}',
                f'Файл {file_name} был удален.\nОписание: {file_description}',
                settings.EMAIL_HOST_USER,
                ['filemanagerforpp@mail.ru']
            )
            email.send()
            logger.info(f"API: Уведомление об удалении файла '{file_name}' успешно отправлено.")
        except Exception as e:
            logger.error(f"API: Ошибка отправки уведомления об удалении файла '{file_name}': {e}")
