from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class FaceUser(models.Model):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    face_encoding = models.TextField()  # Store face encoding as JSON string
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_superadmin = models.BooleanField(default=False)  # Super admin flag

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'users'


class RecognitionLog(models.Model):
    user = models.ForeignKey(FaceUser, on_delete=models.CASCADE)
    confidence = models.FloatField()
    detected_at = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.confidence:.2f} - {self.detected_at}"

    class Meta:
        db_table = 'recognition_logs'
        ordering = ['-detected_at']


class LoginSession(models.Model):
    user = models.ForeignKey(FaceUser, on_delete=models.CASCADE)
    login_time = models.DateTimeField(default=timezone.now)
    logout_time = models.DateTimeField(null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.login_time}"

    class Meta:
        db_table = 'login_sessions'
        ordering = ['-login_time']