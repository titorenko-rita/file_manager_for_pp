from rest_framework import serializers
from .models import StoredFile

class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StoredFile
        fields = '__all__'
        read_only_fields = ('user',) 