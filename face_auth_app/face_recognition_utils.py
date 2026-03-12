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
        """Extract face encoding from image using face_recognition library"""
        try:
            # Convert image to RGB if it's BGR
            if len(image.shape) == 3 and image.shape[2] == 3:
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                image_rgb = image
                
            # Find face locations
            face_locations = face_recognition.face_locations(image_rgb)
            
            if not face_locations:
                return None
                
            # Extract face encodings
            face_encodings = face_recognition.face_encodings(image_rgb, face_locations)
            
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
            return np.array(json.loads(face_encoding_json))
        except:
            return None
    
    def compare_faces(self, known_encoding, unknown_encoding):
        """Compare two face encodings and return similarity score"""
        try:
            if known_encoding is None or unknown_encoding is None:
                return 0.0
                
            # Use face_recognition's compare_faces function
            matches = face_recognition.compare_faces([known_encoding], unknown_encoding, tolerance=0.6)
            
            if matches[0]:
                # Calculate face distance (lower is better)
                face_distance = face_recognition.face_distance([known_encoding], unknown_encoding)[0]
                
                # Convert distance to confidence (0-1, higher is better)
                confidence = 1 - face_distance
                
                return max(0.0, min(1.0, confidence))
            
            return 0.0
            
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
        """Process multiple frames and return average encoding"""
        encodings = []
        
        for frame in frames:
            encoding = self.extract_face_encoding(frame)
            if encoding is not None:
                encodings.append(encoding)
        
        if not encodings:
            return None
            
        # Return average encoding
        return np.mean(encodings, axis=0)
    
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