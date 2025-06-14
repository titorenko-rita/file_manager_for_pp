from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class MLRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    input_data = models.JSONField()
    result = models.JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
