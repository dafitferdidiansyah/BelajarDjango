from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_view, name='chat'),
    path('api/chat/', views.api_chat_view, name='api_chat_view'),
]
