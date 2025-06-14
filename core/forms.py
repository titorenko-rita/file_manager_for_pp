from django import forms
from .models import StoredFile

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = StoredFile
        fields = ['file', 'description']
        labels = {
            'file': 'Файл',
            'description': 'Описание',
        }

class EmailForm(forms.Form):
    to_email = forms.EmailField(label='Email получателя')
    subject = forms.CharField(label='Тема', max_length=100)
    message = forms.CharField(label='Сообщение', widget=forms.Textarea)
    selected_file = forms.ModelChoiceField(
        queryset=StoredFile.objects.all(),
        label='Выберите файл',
        required=False,
        empty_label="Без прикрепления файла"
    ) 