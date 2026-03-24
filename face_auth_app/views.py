import json
import base64
import cv2
import numpy as np
import socket
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from django.db import models
from .models import FaceUser, RecognitionLog, LoginSession
from .face_recognition_utils import FaceRecognitionService
from .decorators import face_auth_required, superadmin_required
import logging

logger = logging.getLogger(__name__)
face_service = FaceRecognitionService()


def get_server_ip():
    """Get the server's actual network IP address"""
    try:
        # Connect to a remote address to determine the local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        # Fallback to localhost if unable to determine network IP
        return "127.0.0.1"


def get_client_ip(request):
    """Get client IP address with enhanced detection for real IPs"""
    # Check for forwarded IP first (for reverse proxies, load balancers)
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # Take the first IP in the chain (original client)
        ip = x_forwarded_for.split(',')[0].strip()
        # Validate it's not a private/local IP
        if not is_private_ip(ip):
            return ip
    
    # Check other proxy headers
    real_ip = request.META.get('HTTP_X_REAL_IP')
    if real_ip and not is_private_ip(real_ip):
        return real_ip
    
    # Check CF-Connecting-IP (Cloudflare)
    cf_ip = request.META.get('HTTP_CF_CONNECTING_IP')
    if cf_ip and not is_private_ip(cf_ip):
        return cf_ip
    
    # Get direct connection IP
    remote_addr = request.META.get('REMOTE_ADDR')
    
    # If it's a local/private connection, try to get a more meaningful IP
    if remote_addr and is_private_ip(remote_addr):
        # For localhost connections, use the server's public IP if available
        if remote_addr in ['127.0.0.1', '::1']:
            public_ip = get_public_ip()
            if public_ip and public_ip != '127.0.0.1':
                return public_ip
            # Fallback to server's network IP
            return get_server_ip()
        else:
            # For local network connections, keep the actual local IP
            # This preserves the real source IP within the network
            return remote_addr
    
    return remote_addr or '127.0.0.1'


def is_private_ip(ip):
    """Check if IP address is private/local"""
    if not ip:
        return True
    
    # Common local/private IP patterns
    private_patterns = [
        '127.',      # Loopback
        '10.',       # Private Class A
        '172.16.',   # Private Class B start
        '172.17.',   # Private Class B
        '172.18.',   # Private Class B
        '172.19.',   # Private Class B
        '172.20.',   # Private Class B
        '172.21.',   # Private Class B
        '172.22.',   # Private Class B
        '172.23.',   # Private Class B
        '172.24.',   # Private Class B
        '172.25.',   # Private Class B
        '172.26.',   # Private Class B
        '172.27.',   # Private Class B
        '172.28.',   # Private Class B
        '172.29.',   # Private Class B
        '172.30.',   # Private Class B
        '172.31.',   # Private Class B end
        '192.168.',  # Private Class C
        '169.254.',  # Link-local
        '::1',       # IPv6 loopback
        'localhost'
    ]
    
    return any(ip.startswith(pattern) for pattern in private_patterns)


def get_public_ip():
    """Get the server's public IP address"""
    try:
        import requests
        # Try multiple services for reliability
        services = [
            'https://api.ipify.org',
            'https://icanhazip.com',
            'https://ipecho.net/plain',
            'https://checkip.amazonaws.com'
        ]
        
        for service in services:
            try:
                response = requests.get(service, timeout=5)
                if response.status_code == 200:
                    ip = response.text.strip()
                    if ip and not is_private_ip(ip):
                        return ip
            except:
                continue
                
    except ImportError:
        # requests not available, skip public IP detection
        pass
    except Exception:
        pass
    
    return None


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
            
            # Fast processing mode - process frames in parallel if possible
            logger.info(f"Processing {len(frames_data)} frames for authentication (fast mode), blink detected: {blink_detected}")
            
            # Process frames with early termination for speed
            frames = []
            max_frames_to_process = min(8, len(frames_data))  # iPhone-like: process max 8 frames
            
            for i, frame_data in enumerate(frames_data[:max_frames_to_process]):
                try:
                    # Decode base64 image
                    image_data = base64.b64decode(frame_data.split(',')[1])
                    nparr = np.frombuffer(image_data, np.uint8)
                    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    if frame is not None:
                        frames.append(frame)
                        
                        # Early exit if we have enough good frames
                        if len(frames) >= 3:  # iPhone-like: 3 good frames is enough
                            break
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
            
            # Fast comparison mode - stop at first confident match (iPhone-like)
            best_match = None
            best_confidence = 0.0
            real_users = FaceUser.objects.filter(is_active=True).exclude(username__startswith='testuser')
            total_users = real_users.count()
            
            logger.info(f"Fast comparing against {total_users} real users (excluding test users)")
            
            # Sort users by recent activity for faster matching (most recent first)
            recent_users = real_users.order_by('-id')  # Most recently registered first
            
            for user in recent_users:
                try:
                    known_encoding = face_service.decode_face_data(user.face_encoding)
                    if known_encoding is not None:
                        confidence = face_service.compare_faces(known_encoding, unknown_encoding)
                        logger.info(f"User {user.username}: confidence = {confidence:.3f}")
                        
                        # iPhone-like: Accept first confident match for speed
                        if confidence >= face_service.confidence_threshold:
                            best_match = user
                            best_confidence = confidence
                            logger.info(f"Fast match found: {user.username} with confidence {confidence:.3f}")
                            break  # Stop searching for speed
                        
                        # Keep track of best match even if below threshold
                        if confidence > best_confidence:
                            best_confidence = confidence
                            best_match = user
                    else:
                        logger.warning(f"User {user.username}: Could not decode face encoding")
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


def debug_page(request):
    """Debug page to check system status"""
    users = FaceUser.objects.all()
    
    # Get IP detection information
    client_ip = get_client_ip(request)
    server_ip = get_server_ip()
    public_ip = get_public_ip()
    
    # Get request headers related to IP
    ip_headers = {
        'REMOTE_ADDR': request.META.get('REMOTE_ADDR'),
        'HTTP_X_FORWARDED_FOR': request.META.get('HTTP_X_FORWARDED_FOR'),
        'HTTP_X_REAL_IP': request.META.get('HTTP_X_REAL_IP'),
        'HTTP_CF_CONNECTING_IP': request.META.get('HTTP_CF_CONNECTING_IP'),
        'HTTP_X_FORWARDED_PROTO': request.META.get('HTTP_X_FORWARDED_PROTO'),
    }
    
    context = {
        'users': users,
        'settings': settings,
        'network_ip': server_ip,
        'server_urls': {
            'network': f'http://{server_ip}:8000',
            'local': 'http://localhost:8000',
        },
        'ip_info': {
            'detected_client_ip': client_ip,
            'server_network_ip': server_ip,
            'server_public_ip': public_ip,
            'is_client_private': is_private_ip(client_ip),
            'headers': ip_headers,
        }
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


# Super Admin Views
@superadmin_required
def superadmin_dashboard(request):
    """Super Admin Dashboard"""
    # Get system statistics
    total_users = FaceUser.objects.count()
    active_users = FaceUser.objects.filter(is_active=True).count()
    superadmins = FaceUser.objects.filter(is_superadmin=True).count()
    total_logins = RecognitionLog.objects.count()
    recent_logins = RecognitionLog.objects.order_by('-detected_at')[:10]
    
    # Get user activity stats
    from django.db.models import Count
    
    # Last 7 days activity
    week_ago = timezone.now() - timedelta(days=7)
    daily_stats = RecognitionLog.objects.filter(
        detected_at__gte=week_ago
    ).extra(
        select={'day': 'date(detected_at)'}
    ).values('day').annotate(
        count=Count('id')
    ).order_by('day')
    
    context = {
        'user': request.face_user,
        'stats': {
            'total_users': total_users,
            'active_users': active_users,
            'inactive_users': total_users - active_users,
            'superadmins': superadmins,
            'total_logins': total_logins,
            'recent_logins': recent_logins,
            'daily_stats': list(daily_stats)
        }
    }
    
    return render(request, 'superadmin.html', context)


@superadmin_required
def manage_users(request):
    """Manage Users with pagination, search, and filtering"""
    if request.method == 'POST':
        action = request.POST.get('action')
        user_id = request.POST.get('user_id')
        
        try:
            user = FaceUser.objects.get(id=user_id)
            
            if action == 'toggle_active':
                user.is_active = not user.is_active
                user.save()
                return JsonResponse({'success': True, 'message': f'User {"activated" if user.is_active else "deactivated"}'})
            
            elif action == 'toggle_superadmin':
                user.is_superadmin = not user.is_superadmin
                user.save()
                return JsonResponse({'success': True, 'message': f'Super admin {"granted" if user.is_superadmin else "revoked"}'})
            
            elif action == 'delete_user':
                username = user.username
                user.delete()
                return JsonResponse({'success': True, 'message': f'User {username} deleted'})
            
            elif action == 'bulk_activate':
                user_ids = request.POST.getlist('user_ids')
                FaceUser.objects.filter(id__in=user_ids).update(is_active=True)
                return JsonResponse({'success': True, 'message': f'{len(user_ids)} users activated'})
            
            elif action == 'bulk_deactivate':
                user_ids = request.POST.getlist('user_ids')
                FaceUser.objects.filter(id__in=user_ids).update(is_active=False)
                return JsonResponse({'success': True, 'message': f'{len(user_ids)} users deactivated'})
            
            elif action == 'bulk_delete':
                user_ids = request.POST.getlist('user_ids')
                # Don't delete current user
                user_ids = [uid for uid in user_ids if int(uid) != request.face_user.id]
                count = FaceUser.objects.filter(id__in=user_ids).count()
                FaceUser.objects.filter(id__in=user_ids).delete()
                return JsonResponse({'success': True, 'message': f'{count} users deleted'})
                
        except FaceUser.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'User not found'})
    
    # Get filter parameters
    search = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', 'all')
    role_filter = request.GET.get('role', 'all')
    sort_by = request.GET.get('sort', '-created_at')
    
    # Build query
    users = FaceUser.objects.all()
    
    # Apply search filter
    if search:
        users = users.filter(
            models.Q(username__icontains=search) | 
            models.Q(email__icontains=search)
        )
    
    # Apply status filter
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    
    # Apply role filter
    if role_filter == 'superadmin':
        users = users.filter(is_superadmin=True)
    elif role_filter == 'regular':
        users = users.filter(is_superadmin=False)
    
    # Apply sorting
    valid_sorts = ['username', '-username', 'email', '-email', 'created_at', '-created_at', 'is_active', '-is_active']
    if sort_by in valid_sorts:
        users = users.order_by(sort_by)
    else:
        users = users.order_by('-created_at')
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(users, 25)  # Show 25 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get statistics
    total_users = FaceUser.objects.count()
    active_users = FaceUser.objects.filter(is_active=True).count()
    superadmins = FaceUser.objects.filter(is_superadmin=True).count()
    
    context = {
        'user': request.face_user,
        'users': page_obj,
        'search': search,
        'status_filter': status_filter,
        'role_filter': role_filter,
        'sort_by': sort_by,
        'stats': {
            'total_users': total_users,
            'active_users': active_users,
            'inactive_users': total_users - active_users,
            'superadmins': superadmins,
            'filtered_count': paginator.count
        }
    }
    
    return render(request, 'manage_users.html', context)


@superadmin_required
def system_logs(request):
    """System Logs"""
    logs = RecognitionLog.objects.select_related('user').order_by('-detected_at')
    
    # Filter options
    user_filter = request.GET.get('user')
    date_filter = request.GET.get('date')
    
    if user_filter:
        logs = logs.filter(user__username__icontains=user_filter)
    
    if date_filter:
        try:
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            logs = logs.filter(detected_at__date=filter_date)
        except ValueError:
            pass
    
    # Pagination
    from django.core.paginator import Paginator
    paginator = Paginator(logs, 50)  # Show 50 logs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'user': request.face_user,
        'logs': page_obj,
        'user_filter': user_filter,
        'date_filter': date_filter,
        'all_users': FaceUser.objects.all().order_by('username')
    }
    
    return render(request, 'system_logs.html', context)
    
@superadmin_required
def add_user_location(request):
    """User IP Location - Show latest session per user only"""
    
    # Use the same IP detection method as logs for accuracy
    detected_ip = get_client_ip(request)
    
    # Get latest log per user (one session per user)
    users_latest_logs = []
    for user in FaceUser.objects.all():
        latest_log = RecognitionLog.objects.filter(user=user).order_by('-detected_at').first()
        if latest_log:  # Only include users who have logged in
            users_latest_logs.append(latest_log)
    
    # Sort by most recent first
    users_latest_logs.sort(key=lambda x: x.detected_at, reverse=True)
    
    context = {
        'user': request.face_user,
        'detected_ip': detected_ip,
        'users_latest_logs': users_latest_logs
    }
    
    return render(request, 'add_user_location.html', context)


@superadmin_required
def redirect_to_server_location(request):
    """Redirect old URL to new server location URL"""
    return redirect('server_location')


@superadmin_required
def export_users(request):
    """Export users to CSV"""
    import csv
    from django.http import HttpResponse
    
    # Get filter parameters (same as manage_users)
    search = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', 'all')
    role_filter = request.GET.get('role', 'all')
    
    # Build query (same logic as manage_users)
    users = FaceUser.objects.all()
    
    if search:
        users = users.filter(
            models.Q(username__icontains=search) | 
            models.Q(email__icontains=search)
        )
    
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    
    if role_filter == 'superadmin':
        users = users.filter(is_superadmin=True)
    elif role_filter == 'regular':
        users = users.filter(is_superadmin=False)
    
    users = users.order_by('username')
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Username', 'Email', 'Status', 'Role', 'Created Date', 'Last Login'])
    
    for user in users:
        # Get last login
        last_log = RecognitionLog.objects.filter(user=user).order_by('-detected_at').first()
        last_login = last_log.detected_at.strftime('%Y-%m-%d %H:%M:%S') if last_log else 'Never'
        
        writer.writerow([
            user.username,
            user.email,
            'Active' if user.is_active else 'Inactive',
            'Super Admin' if user.is_superadmin else 'Regular User',
            user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            last_login
        ])
    
    return response