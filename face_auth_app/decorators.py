from functools import wraps
from django.shortcuts import redirect
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta
from .models import FaceUser


def face_auth_required(view_func):
    """
    Decorator to require face authentication for views
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        try:
            # Check if user is authenticated
            user_id = request.session.get('user_id')
            
            if not user_id:
                return redirect('login')
            
            # Check session timeout
            last_activity = request.session.get('last_activity')
            if last_activity:
                try:
                    last_activity = timezone.datetime.fromisoformat(last_activity)
                    if timezone.now() - last_activity > timedelta(minutes=30):
                        # Session expired
                        request.session.flush()
                        return redirect('login')
                except (ValueError, TypeError):
                    # Invalid timestamp, clear session
                    request.session.flush()
                    return redirect('login')
            
            # Update last activity
            request.session['last_activity'] = timezone.now().isoformat()
            
            # Verify user still exists and is active
            try:
                user = FaceUser.objects.get(id=user_id, is_active=True)
                # Store user in request for easy access
                request.face_user = user
            except FaceUser.DoesNotExist:
                # User doesn't exist or is inactive, clear session
                request.session.flush()
                return redirect('login')
            
            return view_func(request, *args, **kwargs)
            
        except Exception as e:
            # Handle any session-related errors
            if 'session' in str(e).lower() or 'SessionInterrupted' in str(e):
                # Session was interrupted, redirect to login
                return redirect('login')
            else:
                # Re-raise other exceptions
                raise e
    
    return wrapper