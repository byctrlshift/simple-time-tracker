from . import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

app_name = 'accounts'
urlpatterns = [
    path('login/', views.login, name='log-in'),
    path('logout/', views.logout, name='log-out'),
    path('user/register/step-1/', views.register_step_1, name='register-step-1'),
    path('user/register/step-2/<int:user_id>', views.register_step_2, name='register-step-2'),
    path('users/', views.user_list, name='user-list'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
