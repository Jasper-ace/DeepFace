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
from .decorators import face_auth_required
import logging

logger = logging.getLogger(__name__)
face_service = FaceRecognitionService()


def home(request):
    """Home page - redirect to login if not authenticated"""
    if 'user_id' in request.session:
        return redirect('dashboard')
    
    # Check if user just logged out and clear the flag
    just_logged_out = request.session.pop('just_logged_out', False)
    
    context = {
        'just_logged_out': just_logged_out
    }
    
    return render(request, 'home.html', context)


def register_page(request):
    """Face registration page"""
    return render(request, 'register.html')


def login_page(request):
    """Face login page"""
    return render(request, 'login.html')


@face_auth_required
def dashboard(request):
    """User dashboard after successful authentication"""
    user = request.face_user  # Set by decorator
    recent_logs = RecognitionLog.objects.filter(user=user)[:10]
    
    context = {
        'user': user,
        'recent_logs': recent_logs,
        'last_login': recent_logs.first().detected_at if recent_logs else None
    }
    
    return render(request, 'dashboard.html', context)


@csrf_exempt
def logout_view(request):
    """Logout user and clear all session data"""
    try:
        was_logged_in = 'user_id' in request.session
        
        if was_logged_in:
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
        
        # Clear all session data
        request.session.flush()
        
        # Handle AJAX requests specifically (not form submissions)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Logged out successfully'})
        
        # For form submissions and regular requests, redirect with logout flag
        if was_logged_in:
            # Create new session to store logout flag temporarily
            request.session['just_logged_out'] = True
            request.session.set_expiry(60)  # Expire in 60 seconds
        
        response = redirect('home')
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        
        return response
        
    except Exception as e:
        # Handle any session-related errors during logout
        logger.error(f"Error during logout: {str(e)}")
        
        # For AJAX requests, return JSON error
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': 'Logged out'})
        
        # For regular requests, redirect to home
        response = redirect('home')
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        
        return response


@csrf_exempt
def register_face(request):
    """Handle face registration"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            email = data.get('email')
            frames_data = data.get('frames', [])
            angles_captured = data.get('angles_captured', {})
            blink_detected = data.get('blink_detected', False)
            
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
            
            # Enhanced liveness validation with Apple Face ID features
            if settings.LIVENESS_DETECTION:
                liveness_passed = face_service.validate_liveness(frames)
                
                # Additional checks for Apple Face ID style registration
                if not blink_detected:
                    logger.warning("No blink detected during registration")
                
                # Check if multiple angles were captured
                required_angles = ['center', 'left', 'right']
                captured_count = sum(1 for angle in required_angles if angles_captured.get(angle, False))
                
                if captured_count < 2:  # Require at least 2 angles
                    logger.warning(f"Only {captured_count} angles captured during registration")
                
                if not liveness_passed:
                    return JsonResponse({
                        'success': False, 
                        'message': 'Please move your head slowly during registration to complete all angles.',
                        'liveness_failed': True
                    })
            
            # Extract face encoding
            face_encoding = face_service.process_multiple_frames(frames)
            
            if face_encoding is None:
                return JsonResponse({'success': False, 'message': 'Could not extract face features. Please ensure good lighting and face visibility.'})
            
            # Save user
            encoded_face_data = face_service.encode_face_data(face_encoding)
            user = FaceUser.objects.create(
                username=username,
                email=email,
                face_encoding=encoded_face_data
            )
            
            logger.info(f"User {username} registered successfully with {len(frames)} frames, blink: {blink_detected}, angles: {angles_captured}")
            
            return JsonResponse({'success': True, 'message': 'Face ID setup complete'})
            
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return JsonResponse({'success': False, 'message': f'Registration failed: {str(e)}'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@csrf_exempt
def authenticate_face(request):
    """Handle face authentication"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            frames_data = data.get('frames', [])
            blink_detected = data.get('blink_detected', False)
            
            if not frames_data:
                return JsonResponse({'success': False, 'message': 'No frames provided'})
            
            logger.info(f"Processing {len(frames_data)} frames for authentication, blink detected: {blink_detected}")
            
            # Process frames
            frames = []
            for i, frame_data in enumerate(frames_data):
                try:
                    # Decode base64 image
                    image_data = base64.b64decode(frame_data.split(',')[1])
                    nparr = np.frombuffer(image_data, np.uint8)
                    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    if frame is not None:
                        frames.append(frame)
                    else:
                        logger.warning(f"Frame {i} could not be decoded")
                except Exception as e:
                    logger.error(f"Error processing frame {i}: {str(e)}")
                    continue
            
            if not frames:
                return JsonResponse({'success': False, 'message': 'No valid frames could be processed'})
            
            logger.info(f"Successfully processed {len(frames)} frames")
            
            # Enhanced liveness validation for Apple Face ID style authentication
            if settings.LIVENESS_DETECTION:
                liveness_passed = face_service.validate_liveness(frames)
                
                # Additional security check for blink detection
                if not blink_detected:
                    logger.warning("No blink detected during authentication")
                    # Still allow authentication but log the warning
                
                if not liveness_passed:
                    return JsonResponse({
                        'success': False, 
                        'message': 'Please look directly at the camera and blink naturally during authentication.',
                        'liveness_failed': True
                    })
            
            # Extract face encoding from frames
            unknown_encoding = face_service.process_multiple_frames(frames)
            
            if unknown_encoding is None:
                return JsonResponse({'success': False, 'message': 'Could not detect face. Please ensure good lighting and face visibility.'})
            
            logger.info("Face encoding extracted successfully")
            
            # Compare with all registered users
            best_match = None
            best_confidence = 0.0
            total_users = FaceUser.objects.filter(is_active=True).count()
            
            logger.info(f"Comparing against {total_users} registered users")
            
            for user in FaceUser.objects.filter(is_active=True):
                try:
                    known_encoding = face_service.decode_face_data(user.face_encoding)
                    if known_encoding is not None:
                        confidence = face_service.compare_faces(known_encoding, unknown_encoding)
                        logger.info(f"User {user.username}: confidence = {confidence:.3f}")
                        
                        if confidence > best_confidence:
                            best_confidence = confidence
                            best_match = user
                except Exception as e:
                    logger.error(f"Error comparing with user {user.username}: {str(e)}")
                    continue
            
            logger.info(f"Best match: {best_match.username if best_match else 'None'}, confidence: {best_confidence:.3f}")
            
            # Check if confidence meets threshold
            if best_match and best_confidence >= face_service.confidence_threshold:
                try:
                    # Create session
                    request.session['user_id'] = best_match.id
                    request.session['last_activity'] = timezone.now().isoformat()
                    
                    # Ensure session is saved and has a key
                    if not request.session.session_key:
                        request.session.create()
                    
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
                        session_key=request.session.session_key or 'no-key',
                        ip_address=get_client_ip(request)
                    )
                    
                    logger.info(f"Authentication successful for user {best_match.username}")
                    
                    return JsonResponse({
                        'success': True,
                        'message': 'Authentication successful',
                        'confidence': best_confidence,
                        'username': best_match.username,
                        'blink_detected': blink_detected
                    })
                except Exception as e:
                    logger.error(f"Error creating session/logs: {str(e)}")
                    return JsonResponse({'success': False, 'message': f'Authentication succeeded but session creation failed: {str(e)}'})
            else:
                return JsonResponse({
                    'success': False,
                    'message': f'Face not recognized. Please try again.',
                    'confidence': best_confidence,
                    'required_confidence': face_service.confidence_threshold
                })
                
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return JsonResponse({'success': False, 'message': f'Authentication failed: {str(e)}'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@face_auth_required
def recognition_logs(request):
    """View recognition logs"""
    user = request.face_user  # Set by decorator
    logs = RecognitionLog.objects.filter(user=user).order_by('-detected_at')
    
    # Calculate statistics
    total_logins = logs.count()
    successful_logins = logs.filter(confidence__gte=0.6).count()  # Use correct threshold
    
    # Calculate average confidence
    if total_logins > 0:
        total_confidence = sum(log.confidence for log in logs)
        avg_confidence = total_confidence / total_logins
    else:
        avg_confidence = 0.0
    
    context = {
        'user': user,
        'logs': logs,
        'stats': {
            'total_logins': total_logins,
            'successful_logins': successful_logins,
            'failed_logins': total_logins - successful_logins,
            'avg_confidence': round(avg_confidence, 2),
            'last_login': logs.first().detected_at if logs.exists() else None
        }
    }
    
    return render(request, 'logs.html', context)


def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def debug_page(request):
    """Debug page to check system status"""
    users = FaceUser.objects.all()
    
    context = {
        'users': users,
        'settings': settings,
    }
    
    return render(request, 'debug.html', context)


@csrf_exempt
def test_system(request):
    """Test system endpoint"""
    try:
        # Check database connection
        user_count = FaceUser.objects.count()
        
        # Check face recognition service
        service_status = "OK"
        try:
            test_service = FaceRecognitionService()
            service_status = f"OK - Threshold: {test_service.confidence_threshold}"
        except Exception as e:
            service_status = f"Error: {str(e)}"
        
        return JsonResponse({
            'success': True,
            'database': 'Connected',
            'users_registered': user_count,
            'face_service': service_status,
            'liveness_detection': settings.LIVENESS_DETECTION,
            'confidence_threshold': settings.FACE_CONFIDENCE_THRESHOLD
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })