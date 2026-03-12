from django.shortcuts import redirect
from django.urls import reverse, NoReverseMatch
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from datetime import timedelta
from .models import FaceUser


class AuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware to handle authentication and prevent access to protected pages
    after logout using browser navigation
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        # URLs that don't require authentication
        public_paths = [
            '/',
            '/login/',
            '/register/',
            '/api/register-face/',
            '/api/authenticate-face/',
            '/api/test-system/',
            '/admin/',
            '/static/',
            '/media/',
        ]
        
        # Check if current URL is public
        current_url = request.path
        is_public = any(current_url.startswith(path) for path in public_paths)
        
        if is_public:
            return None
        
        # Check if user is authenticated
        user_id = request.session.get('user_id')
        
        if not user_id:
            # User not logged in, redirect to login
            return redirect('/login/')
        
        # Check session timeout
        last_activity = request.session.get('last_activity')
        if last_activity:
            try:
                last_activity = timezone.datetime.fromisoformat(last_activity)
                if timezone.now() - last_activity > timedelta(minutes=30):
                    # Session expired
                    request.session.flush()
                    return redirect('/login/')
            except (ValueError, TypeError):
                # Invalid timestamp, clear session
                request.session.flush()
                return redirect('/login/')
        
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
            return redirect('/login/')
        
        return None
    
    def process_response(self, request, response):
        # Add cache control headers to prevent caching of protected pages
        if hasattr(request, 'face_user'):
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        
        return response