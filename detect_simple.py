import cv2
import numpy as np
import time

class SimpleEmotionDetector:
    def __init__(self):
        """
        Simple emotion detection using OpenCV cascades
        """
        print("🚀 Loading simple emotion detector...")
        
        # Load cascades
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
        # Colors
        self.colors = {
            'happy': (0, 255, 0),      # Green
            'sad': (0, 0, 255),        # Red
            'neutral': (255, 255, 0),  # Cyan
        }
        
        print("✅ Simple detector ready!")
    
    def detect_emotion(self, face_roi, face_gray):
        """
        Simple emotion detection logic
        """
        try:
            h, w = face_gray.shape
            
            # Detect smiles
            smiles = self.smile_cascade.detectMultiScale(
                face_gray, 
                scaleFactor=1.7, 
                minNeighbors=22,
                minSize=(25, 25)
            )
            
            # Detect eyes
            eyes = self.eye_cascade.detectMultiScale(face_gray, 1.1, 5)
            
            # Simple logic
            if len(smiles) > 0:
                return 'happy', 0.8
            elif len(eyes) >= 2:
                # Check face brightness patterns for sadness
                upper_half = face_gray[:h//2, :]
                lower_half = face_gray[h//2:, :]
                
                upper_brightness = np.mean(upper_half)
                lower_brightness = np.mean(lower_half)
                
                if upper_brightness > lower_brightness * 1.1:
                    return 'sad', 0.6
                else:
                    return 'neutral', 0.5
            else:
                return 'neutral', 0.4
                
        except Exception as e:
            return 'neutral', 0.0
    
    def run_detection(self):
        """
        Run emotion detection
        """
        print("🎥 Starting camera...")
        
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        
        if not cap.isOpened():
            print("❌ Could not open camera")
            return
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame = cv2.flip(frame, 1)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # Detect faces
                faces = self.face_cascade.detectMultiScale(gray, 1.1, 5)
                
                for (x, y, w, h) in faces:
                    # Extract face
                    face_roi = frame[y:y+h, x:x+w]
                    face_gray = gray[y:y+h, x:x+w]
                    
                    # Detect emotion
                    emotion, confidence = self.detect_emotion(face_roi, face_gray)
                    
                    # Draw results
                    color = self.colors[emotion]
                    cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                    
                    label = f"{emotion.upper()}: {confidence:.2f}"
                    cv2.putText(frame, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                    
                    # Add emoji
                    if emotion == 'happy':
                        cv2.putText(frame, "😊", (x+w-30, y+30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                    elif emotion == 'sad':
                        cv2.putText(frame, "😢", (x+w-30, y+30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                
                cv2.imshow('Simple Emotion Detection', frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        
        finally:
            cap.release()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    detector = SimpleEmotionDetector()
    detector.run_detection()