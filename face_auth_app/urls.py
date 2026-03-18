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
    
    # Super Admin URLs
    path('superadmin/', views.superadmin_dashboard, name='superadmin'),
    path('superadmin/users/', views.manage_users, name='manage_users'),
    path('superadmin/users/export/', views.export_users, name='export_users'),
    path('superadmin/location/', views.add_user_location, name='server_location'),
    path('superadmin/logs/', views.system_logs, name='system_logs'),
    
    # Redirect old URL to new one
    path('superadmin/users/add/', views.redirect_to_server_location, name='redirect_old_location'),
    
    # API endpoints
    path('api/register-face/', views.register_face, name='register_face'),
    path('api/authenticate-face/', views.authenticate_face, name='authenticate_face'),
    path('api/test-system/', views.test_system, name='test_system'),
]