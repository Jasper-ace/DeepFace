from django.contrib import admin
from .models import FaceUser, RecognitionLog, LoginSession


@admin.register(FaceUser)
class FaceUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['username', 'email']
    readonly_fields = ['face_encoding', 'created_at']


@admin.register(RecognitionLog)
class RecognitionLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'confidence', 'detected_at', 'ip_address']
    list_filter = ['detected_at']
    search_fields = ['user__username']
    readonly_fields = ['detected_at']


@admin.register(LoginSession)
class LoginSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'login_time', 'logout_time', 'ip_address']
    list_filter = ['login_time', 'logout_time']
    search_fields = ['user__username']
    readonly_fields = ['login_time']