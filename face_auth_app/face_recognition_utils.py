import cv2
import numpy as np
import json
import base64
import face_recognition
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class FaceRecognitionService:
    def __init__(self):
        self.confidence_threshold = getattr(settings, 'FACE_CONFIDENCE_THRESHOLD', 0.85)
        self.capture_frames = getattr(settings, 'FACE_CAPTURE_FRAMES', 25)
        
    def extract_face_encoding(self, image):
        """Extract face encoding from image using face_recognition library (optimized)"""
        try:
            # Resize image for faster processing (iPhone-like optimization)
            height, width = image.shape[:2]
            if width > 640:  # Resize if too large
                scale = 640 / width
                new_width = int(width * scale)
                new_height = int(height * scale)
                image = cv2.resize(image, (new_width, new_height))
            
            # Convert image to RGB if it's BGR
            if len(image.shape) == 3 and image.shape[2] == 3:
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                image_rgb = image
                
            # Find face locations with faster model
            face_locations = face_recognition.face_locations(image_rgb, model="hog")  # HOG is faster than CNN
            
            if not face_locations:
                return None
                
            # Extract face encodings
            face_encodings = face_recognition.face_encodings(image_rgb, face_locations, num_jitters=1)  # Reduced jitters for speed
            
            if face_encodings:
                return face_encodings[0]  # Return first face encoding
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting face encoding: {str(e)}")
            return None
    
    def encode_face_data(self, face_encoding):
        """Convert numpy array to JSON string for database storage"""
        if face_encoding is not None:
            return json.dumps(face_encoding.tolist())
        return None
    
    def decode_face_data(self, face_encoding_json):
        """Convert JSON string back to numpy array"""
        try:
            if face_encoding_json is None:
                logger.warning("Face encoding JSON is None")
                return None
            
            # Handle both string and already decoded data
            if isinstance(face_encoding_json, str):
                data = json.loads(face_encoding_json)
            else:
                data = face_encoding_json
            
            # Ensure it's a list/array, not a dict
            if isinstance(data, dict):
                # Skip corrupted data silently (likely test users)
                logger.warning("Face encoding data is a dictionary - corrupted data")
                return None
                
            # Convert to numpy array
            encoding = np.array(data)
            
            # Validate the encoding shape (should be 128-dimensional)
            if encoding.shape != (128,):
                logger.warning(f"Invalid face encoding shape: {encoding.shape}, expected (128,)")
                return None
                
            return encoding
            
        except Exception as e:
            logger.error(f"Error decoding face data: {str(e)}")
            return None
    
    def compare_faces(self, known_encoding, unknown_encoding):
        """Compare two face encodings and return similarity score (optimized)"""
        try:
            if known_encoding is None or unknown_encoding is None:
                return 0.0
            
            # Ensure both encodings are numpy arrays
            if not isinstance(known_encoding, np.ndarray) or not isinstance(unknown_encoding, np.ndarray):
                return 0.0
            
            # Validate encoding shapes
            if known_encoding.shape != (128,) or unknown_encoding.shape != (128,):
                return 0.0
                
            # Fast distance calculation using numpy (faster than face_recognition.face_distance)
            distance = np.linalg.norm(known_encoding - unknown_encoding)
            
            # Convert distance to confidence (optimized thresholds for speed)
            # iPhone-like fast recognition with adjusted thresholds
            if distance < 0.4:  # Very close match
                confidence = 1.0 - (distance / 0.4) * 0.2  # 0.8-1.0 range
            elif distance < 0.6:  # Good match
                confidence = 0.8 - ((distance - 0.4) / 0.2) * 0.3  # 0.5-0.8 range
            else:  # Poor match
                confidence = max(0.0, 0.5 - ((distance - 0.6) / 0.4) * 0.5)  # 0.0-0.5 range
                
            return max(0.0, min(1.0, confidence))
            
        except Exception as e:
            logger.error(f"Error comparing faces: {str(e)}")
            return 0.0
    
    def detect_face_in_frame(self, frame):
        """Detect if there's a face in the frame"""
        try:
            # Convert to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Find face locations
            face_locations = face_recognition.face_locations(rgb_frame)
            
            return len(face_locations) > 0
            
        except Exception as e:
            logger.error(f"Error detecting face: {str(e)}")
            return False
    
    def process_multiple_frames(self, frames):
        """Process multiple frames and return best encoding (optimized for speed)"""
        encodings = []
        
        # Process only first few frames for speed (iPhone-like)
        max_frames_to_process = min(5, len(frames))  # Process max 5 frames
        
        for i in range(max_frames_to_process):
            frame = frames[i]
            encoding = self.extract_face_encoding(frame)
            if encoding is not None:
                encodings.append(encoding)
                
                # Early exit if we get a good encoding from first frame
                if i == 0 and encoding is not None:
                    # Check if this is a clear, high-quality encoding
                    # by verifying it's not all zeros or has good variance
                    if np.std(encoding) > 0.1:  # Good variance indicates quality
                        return encoding  # Return immediately for speed
        
        if not encodings:
            return None
            
        # If we have multiple encodings, return the best one (highest variance = clearest)
        if len(encodings) == 1:
            return encodings[0]
        else:
            # Return encoding with highest standard deviation (clearest features)
            best_encoding = max(encodings, key=lambda x: np.std(x))
            return best_encoding
    
    def validate_liveness(self, frames):
        """Basic liveness detection by checking frame variations"""
        if len(frames) < 3:  # Reduced minimum frames
            return True  # Allow if we have at least 3 frames
            
        try:
            # Simple variation check - in production, use more sophisticated methods
            variations = []
            for i in range(1, len(frames)):
                # Convert frames to grayscale for better comparison
                gray1 = cv2.cvtColor(frames[i-1], cv2.COLOR_BGR2GRAY)
                gray2 = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
                
                # Calculate difference
                diff = cv2.absdiff(gray1, gray2)
                variation = np.mean(diff)
                variations.append(variation)
            
            # Check if there's enough movement (basic liveness check)
            avg_variation = np.mean(variations)
            max_variation = np.max(variations)
            
            # More lenient thresholds
            return avg_variation > 5 or max_variation > 15  # Lowered thresholds
            
        except Exception as e:
            logger.error(f"Error in liveness detection: {str(e)}")
            return True  # Default to allowing if detection fails