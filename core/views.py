from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import gettext_lazy as _ # Импортируем функцию перевода
from .forms import FileUploadForm, EmailForm # Импортируем обе формы
from .models import StoredFile # Импортируем модель StoredFile
import os # Импортируем модуль os для работы с файлами

# Create your views here.

def upload_file(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('file_list') # Редирект на список файлов
    else:
        form = FileUploadForm()
    return render(request, 'core/upload.html', {'form': form})

def file_list(request):
    files = StoredFile.objects.all() # Получаем все файлы из базы данных
    return render(request, 'core/list.html', {'files': files})

def replace_file(request, file_id):
    file_instance = get_object_or_404(StoredFile, id=file_id) # Получаем объект файла или 404 ошибку
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES, instance=file_instance)
        if form.is_valid():
            # Удаляем старый файл с диска перед сохранением нового
            if file_instance.file:
                old_file_path = os.path.join(settings.MEDIA_ROOT, file_instance.file.name)
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)

            form.save() # Сохраняем новую информацию о файле
            return redirect('file_list') # Редирект на список файлов
    else:
        form = FileUploadForm(instance=file_instance)
    return render(request, 'core/replace.html', {'form': form, 'file_instance': file_instance})

def send_report(request):
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            to_email = form.cleaned_data['to_email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            from_email = settings.EMAIL_HOST_USER # Используем email, указанный в settings

            try:
                send_mail(
                    subject,
                    message,
                    from_email,
                    [to_email],
                    fail_silently=False,
                )
                # Можно добавить сообщение об успешной отправке
                return redirect('file_list') # Редирект на список файлов после отправки
            except Exception as e:
                # Можно добавить сообщение об ошибке отправки
                print(f"Ошибка отправки email: {e}") # Для отладки
    else:
        form = EmailForm()
    return render(request, 'core/email_form.html', {'form': form})

def delete_file(request, file_id):
    file_instance = get_object_or_404(StoredFile, id=file_id)
    if request.method == 'POST':
        # Удаляем файл с диска перед удалением из базы данных
        if file_instance.file:
            file_path = os.path.join(settings.MEDIA_ROOT, file_instance.file.name)
            if os.path.exists(file_path):
                os.remove(file_path)

        file_instance.delete() # Удаляем объект из базы данных
        return redirect('file_list')
    # Для простоты, при GET запросе можно сразу отобразить форму подтверждения или удалить
    # Сейчас реализуем просто удаление при GET (можно доработать с шаблоном подтверждения)
    if file_instance.file:
        file_path = os.path.join(settings.MEDIA_ROOT, file_instance.file.name)
        if os.path.exists(file_path):
            os.remove(file_path)

    file_instance.delete()
    return redirect('file_list')
