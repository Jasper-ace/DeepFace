import json
import base64
import cv2
import numpy as np
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from .models import FaceUser, RecognitionLog, LoginSession
from .face_recognition_utils import FaceRecognitionService
import logging

logger = logging.getLogger(__name__)
face_service = FaceRecognitionService()


def home(request):
    """Home page - redirect to login if not authenticated"""
    if 'user_id' in request.session:
        return redirect('dashboard')
    return render(request, 'home.html')


def register_page(request):
    """Face registration page"""
    return render(request, 'register.html')


def login_page(request):
    """Face login page"""
    return render(request, 'login.html')


def dashboard(request):
    """User dashboard after successful authentication"""
    if 'user_id' not in request.session:
        return redirect('login')
    
    try:
        user = FaceUser.objects.get(id=request.session['user_id'])
        recent_logs = RecognitionLog.objects.filter(user=user)[:10]
        
        context = {
            'user': user,
            'recent_logs': recent_logs,
            'last_login': recent_logs.first().detected_at if recent_logs else None
        }
        
        return render(request, 'dashboard.html', context)
        
    except FaceUser.DoesNotExist:
        del request.session['user_id']
        return redirect('login')


def logout_view(request):
    """Logout user"""
    if 'user_id' in request.session:
        try:
            # Update logout time in session
            session = LoginSession.objects.filter(
                user_id=request.session['user_id'],
                session_key=request.session.session_key,
                logout_time__isnull=True
            ).first()
            
            if session:
                session.logout_time = timezone.now()
                session.save()
                
        except Exception as e:
            logger.error(f"Error updating logout time: {str(e)}")
        
        del request.session['user_id']
    
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


@csrf_exempt
def register_face(request):
    """Handle face registration"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            email = data.get('email')
            frames_data = data.get('frames', [])
            
            if not username or not email or not frames_data:
                return JsonResponse({'success': False, 'message': 'Missing required data'})
            
            # Check if user already exists
            if FaceUser.objects.filter(username=username).exists():
                return JsonResponse({'success': False, 'message': 'Username already exists'})
            
            if FaceUser.objects.filter(email=email).exists():
                return JsonResponse({'success': False, 'message': 'Email already exists'})
            
            # Process frames
            frames = []
            for frame_data in frames_data:
                # Decode base64 image
                image_data = base64.b64decode(frame_data.split(',')[1])
                nparr = np.frombuffer(image_data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                frames.append(frame)
            
            # Validate liveness
            if settings.LIVENESS_DETECTION and not face_service.validate_liveness(frames):
                return JsonResponse({'success': False, 'message': 'Liveness detection failed'})
            
            # Extract face encoding
            face_encoding = face_service.process_multiple_frames(frames)
            
            if face_encoding is None:
                return JsonResponse({'success': False, 'message': 'Could not extract face features'})
            
            # Save user
            encoded_face_data = face_service.encode_face_data(face_encoding)
            user = FaceUser.objects.create(
                username=username,
                email=email,
                face_encoding=encoded_face_data
            )
            
            return JsonResponse({'success': True, 'message': 'Registration successful'})
            
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return JsonResponse({'success': False, 'message': 'Registration failed'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@csrf_exempt
def authenticate_face(request):
    """Handle face authentication"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            frames_data = data.get('frames', [])
            
            if not frames_data:
                return JsonResponse({'success': False, 'message': 'No frames provided'})
            
            # Process frames
            frames = []
            for frame_data in frames_data:
                # Decode base64 image
                image_data = base64.b64decode(frame_data.split(',')[1])
                nparr = np.frombuffer(image_data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                frames.append(frame)
            
            # Validate liveness
            if settings.LIVENESS_DETECTION and not face_service.validate_liveness(frames):
                return JsonResponse({'success': False, 'message': 'Liveness detection failed'})
            
            # Extract face encoding from frames
            unknown_encoding = face_service.process_multiple_frames(frames)
            
            if unknown_encoding is None:
                return JsonResponse({'success': False, 'message': 'Could not detect face'})
            
            # Compare with all registered users
            best_match = None
            best_confidence = 0.0
            
            for user in FaceUser.objects.filter(is_active=True):
                known_encoding = face_service.decode_face_data(user.face_encoding)
                if known_encoding is not None:
                    confidence = face_service.compare_faces(known_encoding, unknown_encoding)
                    
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_match = user
            
            # Check if confidence meets threshold
            if best_match and best_confidence >= face_service.confidence_threshold:
                # Create session
                request.session['user_id'] = best_match.id
                
                # Log recognition
                RecognitionLog.objects.create(
                    user=best_match,
                    confidence=best_confidence,
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                # Create login session
                LoginSession.objects.create(
                    user=best_match,
                    session_key=request.session.session_key,
                    ip_address=get_client_ip(request)
                )
                
                return JsonResponse({
                    'success': True,
                    'message': 'Authentication successful',
                    'confidence': best_confidence,
                    'username': best_match.username
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Face not recognized',
                    'confidence': best_confidence
                })
                
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return JsonResponse({'success': False, 'message': 'Authentication failed'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


def recognition_logs(request):
    """View recognition logs"""
    if 'user_id' not in request.session:
        return redirect('login')
    
    try:
        user = FaceUser.objects.get(id=request.session['user_id'])
        logs = RecognitionLog.objects.filter(user=user).order_by('-detected_at')
        
        context = {
            'user': user,
            'logs': logs
        }
        
        return render(request, 'logs.html', context)
        
    except FaceUser.DoesNotExist:
        del request.session['user_id']
        return redirect('login')


def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip