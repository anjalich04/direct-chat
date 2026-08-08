from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.get_users_list, name='get_users_list'),
    path('messages/<int:user_id>/', views.get_chat_history, name='get_chat_history'),
    path('messages/<int:other_user_id>/read', views.mark_messages_as_read, name='mark_messages_as_read'),
    path('messages/<int:other_user_id>/read/', views.mark_messages_as_read, name='mark_messages_as_read_slash'),
    path('send/', views.send_message, name='send_message'),
]
