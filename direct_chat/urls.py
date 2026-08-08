from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from chat import views as chat_views
from accounts import views as account_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/users', chat_views.get_users_list, name='api_users'),
    path('api/users/', chat_views.get_users_list, name='api_users_slash'),
    path('api/messages/<int:other_user_id>/read', chat_views.mark_messages_as_read, name='api_mark_read'),
    path('api/messages/<int:other_user_id>/read/', chat_views.mark_messages_as_read, name='api_mark_read_slash'),
    path('chat/', include('chat.urls')),
    path('', account_views.home_view, name='home'),
    path('', include('accounts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
