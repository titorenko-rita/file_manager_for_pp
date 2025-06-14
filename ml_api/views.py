from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import MLRequest

# Create your views here.

class MLPredictView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Сохраняем запрос пользователя
        ml_request = MLRequest.objects.create(
            user=request.user,
            input_data=request.data,
            result=None
        )
        return Response({"status": "ok", "request_id": ml_request.id}, status=status.HTTP_201_CREATED)
