from django.db import models

# Create your models here.

class StoredFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.file.name} ({self.uploaded_at})"
