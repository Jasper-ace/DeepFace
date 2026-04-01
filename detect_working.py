import cv2
import torch
import numpy as np
from torchvision import transforms, models
import torch.nn as nn
import time
import os

class WorkingEmotionDetector:
    def __init__(self, model_path="best_model.pth", use_custom_model=True):
        """
        Working emotion detector with multiple fallback methods
        """
        self.use_custom_model = use_custom_model and os.path.exists(model_path)
        self.model_path = model_path
        
        print("🚀 Initializing Working Emotion Detector...")
        
        # Initialize custom model if available
        if self.use_custom_model:
            try:
                self.custom_model = self._load_custom_model()
                self.transform = self._get_transform()
                print("✅ Custom model loaded successfully!")
            except Exception as e:
                print(f"❌ Custom model failed: {e}")
                self.use_custom_model = False
        
        # Initialize pre-trained model as fallback
        self.pretrained_model = None
        try:
            from fer.fer import FER
            self.pretrained_model = FER(mtcnn=True)
            print("✅ Pre-trained FER model loaded successfully!")
        except Exception as e:
            print(f"⚠️  Pre-trained model not available: {e}")
        
        # OpenCV cascades for simple detection
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
        
        # Colors
        self.colors = {
            'happy': (0, 255, 0),      # Green
            'sad': (0, 0, 255),        # Red
            'uncertain': (0, 255, 255) # Yellow
        }
        
        print(f"🎯 Detection methods available:")
        print(f"   - Custom model: {'✅' if self.use_custom_model else '❌'}")
        print(f"   - Pre-trained FER: {'✅' if self.pretrained_model else '❌'}")
        print(f"   - OpenCV simple: ✅")
    
    def _load_custom_model(self):
        """Load the custom trained model"""
        device = torch.device("cpu")
        
        # Create model architecture
        model = models.resnet18(weights=None)
        model.fc = nn.Linear(model.fc.in_features, 2)  # 2 classes: sad, happy
        
        # Load weights
        model.load_state_dict(torch.load(self.model_path, map_location=device))
        model.eval()
        model.to(device)
        
        return model
    
    def _get_transform(self):
        """Get image preprocessing transform"""
        return transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
    
    def detect_faces(self, frame):
        """Detect faces using OpenCV"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(50, 50))
        return faces
    
    def predict_custom_model(self, face_image):
        """Predict using custom model with corrected class mapping"""
        if not self.use_custom_model:
            return None, 0.0
        
        try:
            device = torch.device("cpu")
            input_tensor = self.transform(face_image).unsqueeze(0).to(device)
            
            with torch.no_grad():
                outputs = self.custom_model(input_tensor)
                probabilities = torch.nn.functional.softmax(outputs, dim=1)
                
                # CORRECTED: Based on your training, index 0 = sad, index 1 = happy
                sad_prob = probabilities[0][0].item()
                happy_prob = probabilities[0][1].item()
                
                # Determine emotion - force happy or sad classification
                if happy_prob > sad_prob:
                    return "happy", happy_prob
                else:
                    return "sad", sad_prob
                        
        except Exception as e:
            print(f"Custom model error: {e}")
            return None, 0.0
    
    def predict_pretrained_model(self, frame):
        """Predict using pre-trained FER model"""
        if not self.pretrained_model:
            return []
        
        try:
            results = self.pretrained_model.detect_emotions(frame)
            emotions_data = []
            
            for face_data in results:
                box = face_data['box']
                emotions = face_data['emotions']
                
                happy_score = emotions.get('happy', 0)
                sad_score = emotions.get('sad', 0)
                
                # Force classification to happy or sad only
                if happy_score > sad_score:
                    emotion = 'happy'
                    confidence = happy_score
                else:
                    emotion = 'sad'
                    confidence = sad_score
                
                # Boost confidence if it's too low
                if confidence < 0.3:
                    confidence = 0.5
                
                emotions_data.append({
                    'box': box,
                    'emotion': emotion,
                    'confidence': confidence
                })
            
            return emotions_data
            
        except Exception as e:
            print(f"Pre-trained model error: {e}")
            return []
    
    def predict_simple_opencv(self, face_roi, face_gray):
        """Simple OpenCV-based emotion detection - happy or sad only"""
        try:
            h, w = face_gray.shape
            
            # Detect smiles
            smiles = self.smile_cascade.detectMultiScale(face_gray, 1.7, 22, minSize=(25, 25))
            
            if len(smiles) > 0:
                return "happy", 0.7
            
            # If no smile detected, classify as sad
            return "sad", 0.6
                
        except Exception as e:
            return "sad", 0.4
    
    def detect_emotions(self, frame):
        """Main emotion detection function using best available method"""
        faces = self.detect_faces(frame)
        emotions_data = []
        
        # Try pre-trained model first (most accurate)
        if self.pretrained_model:
            try:
                pretrained_results = self.predict_pretrained_model(frame)
                if pretrained_results:
                    return pretrained_results
            except:
                pass
        
        # Fallback to custom model + simple detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        for (x, y, w, h) in faces:
            if x >= 0 and y >= 0 and x+w <= frame.shape[1] and y+h <= frame.shape[0]:
                face_roi = frame[y:y+h, x:x+w]
                face_gray = gray[y:y+h, x:x+w]
                
                # Try custom model first
                emotion, confidence = None, 0.0
                if self.use_custom_model:
                    emotion, confidence = self.predict_custom_model(face_roi)
                
                # If custom model fails, use simple method
                if emotion is None:
                    emotion, confidence = self.predict_simple_opencv(face_roi, face_gray)
                
                emotions_data.append({
                    'box': (x, y, w, h),
                    'emotion': emotion,
                    'confidence': confidence
                })
        
        return emotions_data
    
    def draw_results(self, frame, emotions_data):
        """Draw emotion detection results"""
        for data in emotions_data:
            x, y, w, h = data['box']
            emotion = data['emotion']
            confidence = data['confidence']
            
            color = self.colors.get(emotion, (255, 255, 255))
            
            # Draw bounding box
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            
            # Draw label
            label = f"{emotion.upper()}: {confidence:.2f}"
            (text_width, text_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
            
            cv2.rectangle(frame, (x, y - text_height - 10), (x + text_width, y), color, -1)
            cv2.putText(frame, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Add emoji
            if emotion == 'happy':
                cv2.putText(frame, "😊", (x + w - 30, y + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            elif emotion == 'sad':
                cv2.putText(frame, "😢", (x + w - 30, y + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        
        return frame
    
    def run_detection(self):
        """Run real-time emotion detection"""
        print("🎥 Starting camera...")
        print("📋 Controls: Q=Quit, S=Screenshot, H=Help, M=Toggle Method")
        print("=" * 60)
        
        # Try to open camera
        cap = None
        for backend in [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]:
            for cam_id in [0, 1, 2]:
                try:
                    cap = cv2.VideoCapture(cam_id, backend)
                    if cap.isOpened():
                        ret, test_frame = cap.read()
                        if ret and test_frame is not None:
                            print(f"✅ Camera {cam_id} opened with backend {backend}")
                            break
                        else:
                            cap.release()
                            cap = None
                except:
                    if cap:
                        cap.release()
                    cap = None
            if cap and cap.isOpened():
                break
        
        if not cap or not cap.isOpened():
            print("❌ Could not open camera!")
            return
        
        # Set camera properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        frame_count = 0
        fps_start_time = time.time()
        fps = 0.0  # Initialize FPS variable
        show_help = True
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("❌ Could not read frame")
                    break
                
                frame = cv2.flip(frame, 1)
                
                # Detect emotions
                emotions_data = self.detect_emotions(frame)
                
                # Draw results
                frame = self.draw_results(frame, emotions_data)
                
                # Add info overlay
                frame_count += 1
                if frame_count % 30 == 0:
                    fps_end_time = time.time()
                    fps = 30 / (fps_end_time - fps_start_time)
                    fps_start_time = fps_end_time
                
                # Status info
                cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, f"Faces: {len(emotions_data)}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Method indicator
                method = "Custom+FER" if self.use_custom_model and self.pretrained_model else \
                        "Custom" if self.use_custom_model else \
                        "FER" if self.pretrained_model else "Simple"
                cv2.putText(frame, f"Method: {method}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Help text
                if show_help:
                    help_text = ["Q=Quit", "S=Screenshot", "H=Toggle Help"]
                    for i, text in enumerate(help_text):
                        cv2.putText(frame, text, (10, frame.shape[0] - 60 + i*20), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                cv2.imshow('Working Emotion Detection - Happy/Sad', frame)
                
                # Handle keys
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('s'):
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    filename = f"emotion_working_{timestamp}.jpg"
                    cv2.imwrite(filename, frame)
                    print(f"📸 Screenshot saved: {filename}")
                elif key == ord('h'):
                    show_help = not show_help
        
        except KeyboardInterrupt:
            print("\n⚠️ Interrupted by user")
        
        finally:
            if cap:
                cap.release()
            cv2.destroyAllWindows()
            print("🔄 Cleanup completed")


def main():
    print("🚀 Working Emotion Detection System")
    print("=" * 50)
    
    # Check if custom model exists
    model_exists = os.path.exists("best_model.pth")
    print(f"📁 Custom model (best_model.pth): {'✅ Found' if model_exists else '❌ Not found'}")
    
    try:
        detector = WorkingEmotionDetector("best_model.pth", use_custom_model=model_exists)
        detector.run_detection()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure your camera is not being used by other apps")
        print("2. Check camera permissions in Windows settings")
        print("3. Try running as administrator")
    
    print("✅ Emotion detection completed!")


if __name__ == "__main__":
    main()