from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_page, name='register'),
    path('login/', views.login_page, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('logs/', views.recognition_logs, name='logs'),
    path('debug/', views.debug_page, name='debug'),
    
    # API endpoints
    path('api/register-face/', views.register_face, name='register_face'),
    path('api/authenticate-face/', views.authenticate_face, name='authenticate_face'),
    path('api/test-system/', views.test_system, name='test_system'),
]