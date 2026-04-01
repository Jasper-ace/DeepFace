import cv2
import numpy as np
import time

class OpenCVEmotionDetector:
    def __init__(self):
        """
        Initialize OpenCV-based emotion detection using facial landmarks
        """
        print("🚀 Initializing OpenCV emotion detection...")
        
        # Load face detection cascade
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Load smile detection cascade
        self.smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
        
        # Load eye detection cascade
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
        # Colors
        self.colors = {
            'happy': (0, 255, 0),      # Green
            'sad': (0, 0, 255),        # Red
            'neutral': (255, 255, 0),  # Cyan
        }
        
        print("✅ OpenCV emotion detector initialized!")
        print("🎯 Uses facial feature analysis for happy/sad detection")
    
    def analyze_face_features(self, face_roi, face_gray):
        """
        Analyze facial features to determine emotion
        """
        try:
            h, w = face_gray.shape
            
            # Detect smiles in the face region
            smiles = self.smile_cascade.detectMultiScale(
                face_gray, 
                scaleFactor=1.8, 
                minNeighbors=20,
                minSize=(25, 25)
            )
            
            # Detect eyes
            eyes = self.eye_cascade.detectMultiScale(
                face_gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(10, 10)
            )
            
            # Calculate features
            smile_score = len(smiles) / max(1, (w * h) / 10000)  # Normalize by face size
            eye_count = len(eyes)
            
            # Analyze face geometry for sadness indicators
            # Check for drooping features (simplified approach)
            
            # Get face regions for analysis
            upper_face = face_gray[:h//2, :]  # Upper half
            lower_face = face_gray[h//2:, :]  # Lower half
            
            # Calculate brightness/contrast differences (sad faces often have different patterns)
            upper_brightness = np.mean(upper_face)
            lower_brightness = np.mean(lower_face)
            brightness_ratio = upper_brightness / max(lower_brightness, 1)
            
            # Simple emotion classification based on features
            emotion = 'neutral'
            confidence = 0.5
            
            if len(smiles) > 0:
                # Strong smile detected
                emotion = 'happy'
                confidence = min(0.9, 0.6 + smile_score * 0.3)
            elif brightness_ratio > 1.2 and eye_count >= 2:
                # Possible sad expression (eyes visible, lower face darker)
                emotion = 'sad'
                confidence = min(0.8, 0.5 + (brightness_ratio - 1.0) * 0.3)
            elif eye_count < 2:
                # Eyes not clearly visible, might indicate squinting (happy) or closed (sad)
                if smile_score > 0:
                    emotion = 'happy'
                    confidence = 0.6
                else:
                    emotion = 'neutral'
                    confidence = 0.4
            
            return emotion, confidence, {
                'smiles': len(smiles),
                'eyes': eye_count,
                'brightness_ratio': brightness_ratio,
                'smile_score': smile_score
            }
            
        except Exception as e:
            print(f"❌ Error analyzing face features: {e}")
            return 'neutral', 0.0, {}
    
    def detect_emotions(self, frame):
        """
        Detect emotions using OpenCV facial feature analysis
        """
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.1, 
                minNeighbors=5, 
                minSize=(50, 50)
            )
            
            emotions_data = []
            
            for (x, y, w, h) in faces:
                # Extract face region
                face_roi = frame[y:y+h, x:x+w]
                face_gray = gray[y:y+h, x:x+w]
                
                # Analyze facial features
                emotion, confidence, features = self.analyze_face_features(face_roi, face_gray)
                
                emotions_data.append({
                    'box': (x, y, w, h),
                    'emotion': emotion,
                    'confidence': confidence,
                    'features': features
                })
            
            return emotions_data
            
        except Exception as e:
            print(f"❌ Error in emotion detection: {e}")
            return []
    
    def draw_results(self, frame, emotions_data):
        """
        Draw emotion detection results
        """
        for data in emotions_data:
            x, y, w, h = data['box']
            emotion = data['emotion']
            confidence = data['confidence']
            features = data['features']
            
            # Get color
            color = self.colors.get(emotion, (255, 255, 255))
            
            # Draw face rectangle
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            
            # Draw emotion label
            label = f"{emotion.upper()}: {confidence:.2f}"
            
            # Background for text
            (text_width, text_height), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2
            )
            
            cv2.rectangle(
                frame, 
                (x, y - text_height - 10), 
                (x + text_width, y), 
                color, 
                -1
            )
            
            # Draw text
            cv2.putText(
                frame, 
                label, 
                (x, y - 5), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.7, 
                (255, 255, 255), 
                2
            )
            
            # Draw feature info
            feature_y = y + h + 20
            for feature_name, feature_value in features.items():
                if isinstance(feature_value, float):
                    feature_text = f"{feature_name}: {feature_value:.2f}"
                else:
                    feature_text = f"{feature_name}: {feature_value}"
                
                cv2.putText(
                    frame, 
                    feature_text, 
                    (x, feature_y), 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    0.4, 
                    (255, 255, 255), 
                    1
                )
                feature_y += 15
            
            # Add emoji
            if emotion == 'happy':
                cv2.putText(frame, "😊", (x + w - 30, y + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            elif emotion == 'sad':
                cv2.putText(frame, "😢", (x + w - 30, y + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            else:
                cv2.putText(frame, "😐", (x + w - 30, y + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        
        return frame
    
    def run_detection(self, camera_id=0):
        """
        Run real-time emotion detection
        """
        print("🎥 Starting OpenCV emotion detection...")
        print("📋 Instructions:")
        print("   - Press 'q' to quit")
        print("   - Press 's' to save screenshot")
        print("=" * 50)
        
        cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
        
        if not cap.isOpened():
            print("❌ Could not open camera")
            return
        
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        frame_count = 0
        fps_start_time = time.time()
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame = cv2.flip(frame, 1)
                
                # Detect emotions
                emotions_data = self.detect_emotions(frame)
                
                # Draw results
                frame = self.draw_results(frame, emotions_data)
                
                # FPS counter
                frame_count += 1
                if frame_count % 30 == 0:
                    fps_end_time = time.time()
                    fps = 30 / (fps_end_time - fps_start_time)
                    fps_start_time = fps_end_time
                
                cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, f"Faces: {len(emotions_data)}", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                cv2.imshow('OpenCV Emotion Detection', frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    filename = f"emotion_opencv_{timestamp}.jpg"
                    cv2.imwrite(filename, frame)
                    print(f"📸 Screenshot saved: {filename}")
        
        except KeyboardInterrupt:
            print("\n⚠️ Interrupted by user")
        
        finally:
            cap.release()
            cv2.destroyAllWindows()


def main():
    print("🚀 OpenCV Emotion Detection System")
    print("=" * 40)
    
    detector = OpenCVEmotionDetector()
    detector.run_detection(camera_id=0)
    
    print("✅ Detection completed!")


if __name__ == "__main__":
    main()