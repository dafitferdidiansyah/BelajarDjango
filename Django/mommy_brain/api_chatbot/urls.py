# api_chatbot/urls.py

from django.urls import path
from .views import ChatbotMommyAPIView

urlpatterns = [
    # URL ini akan cocok dengan: http://127.0.0.1:8000/api/chat/
    path('chat/', ChatbotMommyAPIView.as_view(), name='chatbot_api'),
]