from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from django.contrib.sessions.exceptions import SessionInterrupted
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)


class SessionExceptionMiddleware(MiddlewareMixin):
    """
    Middleware to handle session interruption exceptions gracefully
    """
    
    def process_exception(self, request, exception):
        """Handle session interruption exceptions"""
        if isinstance(exception, SessionInterrupted):
            logger.warning(f"Session interrupted for path: {request.path}")
            
            # Check if this is an AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'message': 'Session expired',
                    'redirect': '/login/'
                }, status=401)
            
            # For regular requests, redirect to login
            return redirect('login')
        
        # Let other exceptions bubble up
        return None