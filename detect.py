import cv2
import torch
import numpy as np
from torchvision import transforms, models
import torch.nn as nn
import time

class EmotionDetector:
    def __init__(self, model_path="best_model.pth", debug_mode=False):
        """
        Initialize the emotion detector with the trained model
        """
        self.device = torch.device("cpu")  # Using CPU for stability
        self.model_path = model_path
        self.debug_mode = debug_mode
        
        # Class names - CORRECTED based on your dataset structure
        # Your training data: Datasets/train/happy and Datasets/train/sad
        # ImageFolder sorts alphabetically: ['happy', 'sad'] -> [0, 1]
        self.class_names = ['happy', 'sad']  # Correct order: 0=happy, 1=sad
        self.num_classes = len(self.class_names)
        
        # Load the model
        self.model = self._load_model()
        
        # Image preprocessing pipeline (same as training)
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406],
                               [0.229, 0.224, 0.225])
        ])
        
        # Face detection cascade
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Colors for visualization
        self.colors = {
            'happy': (0, 255, 0),      # Green
            'sad': (0, 0, 255),        # Red
            'uncertain': (0, 255, 255), # Yellow
            'unknown': (128, 128, 128)  # Gray
        }
        
        print("✅ Emotion Detector initialized successfully!")
        print(f"📱 Model loaded from: {model_path}")
        print(f"🎯 Classes: {self.class_names}")
        if self.debug_mode:
            print("🐛 Debug mode enabled - will show prediction details")
    
    def _load_model(self):
        """
        Load the trained ResNet18 model
        """
        try:
            # Create model architecture (same as training)
            model = models.resnet18(weights=None)  # Don't load pretrained weights
            
            # Modify the final layer for our classes
            model.fc = nn.Linear(model.fc.in_features, self.num_classes)
            
            # Load the trained weights
            model.load_state_dict(torch.load(self.model_path, map_location=self.device))
            model.eval()
            model.to(self.device)
            
            print("✅ Model loaded successfully!")
            return model
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            print("💡 Make sure 'best_model.pth' exists in the current directory")
            raise
    
    def detect_faces(self, frame):
        """
        Detect faces in the frame using OpenCV
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1, 
            minNeighbors=5, 
            minSize=(50, 50)
        )
        return faces
    
    def predict_emotion(self, face_image):
        """
        Predict emotion from a face image with improved logic
        """
        try:
            # Preprocess the image
            input_tensor = self.transform(face_image).unsqueeze(0).to(self.device)
            
            # Make prediction
            with torch.no_grad():
                outputs = self.model(input_tensor)
                probabilities = torch.nn.functional.softmax(outputs, dim=1)
                
                # Get probabilities for both classes
                # CORRECTED: index 0 = happy, index 1 = sad (alphabetical order)
                happy_prob = probabilities[0][0].item()
                sad_prob = probabilities[0][1].item()
                
                # Debug mode: print all probabilities
                if self.debug_mode:
                    print(f"🐛 Raw outputs: {outputs.cpu().numpy()}")
                    print(f"🐛 Probabilities: sad={sad_prob:.3f}, happy={happy_prob:.3f}")
                
                # Determine emotion with confidence threshold
                confidence_threshold = 0.6  # Require at least 60% confidence
                
                if happy_prob > sad_prob:
                    if happy_prob > confidence_threshold:
                        emotion = "happy"
                        confidence_score = happy_prob
                    else:
                        emotion = "uncertain"
                        confidence_score = happy_prob
                else:
                    if sad_prob > confidence_threshold:
                        emotion = "sad"
                        confidence_score = sad_prob
                    else:
                        emotion = "uncertain"
                        confidence_score = sad_prob
                
                # If the difference is too small, mark as uncertain
                if abs(happy_prob - sad_prob) < 0.2:  # Less than 20% difference
                    emotion = "uncertain"
                    confidence_score = max(happy_prob, sad_prob)
                
                if self.debug_mode:
                    print(f"🐛 Final prediction: {emotion} ({confidence_score:.3f})")
                
                return emotion, confidence_score
                
        except Exception as e:
            print(f"❌ Error in emotion prediction: {e}")
            return "unknown", 0.0
    
    def draw_results(self, frame, faces, emotions_data):
        """
        Draw bounding boxes and emotion labels on the frame
        """
        for i, (x, y, w, h) in enumerate(faces):
            if i < len(emotions_data):
                emotion, confidence = emotions_data[i]
                color = self.colors.get(emotion, self.colors['unknown'])
                
                # Draw face bounding box
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                
                # Prepare label text
                label = f"{emotion.upper()}: {confidence:.2f}"
                
                # Calculate text size for background
                (text_width, text_height), baseline = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2
                )
                
                # Draw background rectangle for text
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
                
                # Add emotion icon
                if emotion == 'happy':
                    cv2.putText(frame, "😊", (x + w - 30, y + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                elif emotion == 'sad':
                    cv2.putText(frame, "😢", (x + w - 30, y + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
                elif emotion == 'uncertain':
                    cv2.putText(frame, "🤔", (x + w - 30, y + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        
        return frame
    
    def run_detection(self, camera_id=0):
        """
        Run real-time emotion detection from camera
        """
        print("🎥 Starting camera...")
        print("📋 Instructions:")
        print("   - Press 'q' to quit")
        print("   - Press 's' to save screenshot")
        print("   - Press 'h' to toggle help")
        print("=" * 50)
        
        # Try multiple camera backends and IDs
        camera_backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
        camera_ids = [0, 1, 2, -1]  # Try different camera IDs
        
        cap = None
        
        # Try different combinations
        for backend in camera_backends:
            for cam_id in camera_ids:
                print(f"🔍 Trying camera {cam_id} with backend {backend}...")
                try:
                    cap = cv2.VideoCapture(cam_id, backend)
                    
                    # Test if camera actually works
                    if cap.isOpened():
                        ret, test_frame = cap.read()
                        if ret and test_frame is not None:
                            print(f"✅ Camera {cam_id} opened successfully with backend {backend}!")
                            break
                        else:
                            cap.release()
                            cap = None
                    else:
                        if cap:
                            cap.release()
                        cap = None
                except Exception as e:
                    print(f"❌ Failed camera {cam_id} with backend {backend}: {e}")
                    if cap:
                        cap.release()
                    cap = None
            
            if cap and cap.isOpened():
                break
        
        # If still no camera, try DirectShow specifically (Windows)
        if not cap or not cap.isOpened():
            print("🔄 Trying DirectShow backend specifically...")
            try:
                cap = cv2.VideoCapture(0 + cv2.CAP_DSHOW)
                if cap.isOpened():
                    ret, test_frame = cap.read()
                    if ret and test_frame is not None:
                        print("✅ DirectShow camera opened successfully!")
                    else:
                        cap.release()
                        cap = None
            except Exception as e:
                print(f"❌ DirectShow failed: {e}")
                if cap:
                    cap.release()
                cap = None
        
        # Final check
        if not cap or not cap.isOpened():
            print("❌ Error: Could not open any camera!")
            print("\n🔧 Troubleshooting tips:")
            print("1. Make sure your camera is not being used by another application")
            print("2. Check if your camera drivers are installed")
            print("3. Try running as administrator")
            print("4. Check Windows Camera privacy settings")
            print("5. Try unplugging and reconnecting USB camera")
            return
        
        # Set camera properties for better performance
        try:
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FPS, 30)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer for real-time
            
            # Get actual camera properties
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            print(f"📷 Camera resolution: {width}x{height}")
            print(f"🎬 Camera FPS: {fps}")
            
        except Exception as e:
            print(f"⚠️  Warning: Could not set camera properties: {e}")
        
        frame_count = 0
        fps_start_time = time.time()
        show_help = True
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret or frame is None:
                    print("❌ Error: Could not read frame from camera")
                    print("🔄 Trying to reconnect...")
                    
                    # Try to reconnect
                    cap.release()
                    time.sleep(1)
                    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                    if not cap.isOpened():
                        print("❌ Could not reconnect to camera")
                        break
                    continue
                
                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                
                # Detect faces
                faces = self.detect_faces(frame)
                
                # Process each face
                emotions_data = []
                for (x, y, w, h) in faces:
                    # Extract face region with bounds checking
                    if x >= 0 and y >= 0 and x+w <= frame.shape[1] and y+h <= frame.shape[0]:
                        face_roi = frame[y:y+h, x:x+w]
                        
                        # Only process if face is large enough
                        if face_roi.shape[0] > 50 and face_roi.shape[1] > 50:
                            # Predict emotion
                            emotion, confidence = self.predict_emotion(face_roi)
                            emotions_data.append((emotion, confidence))
                        else:
                            emotions_data.append(("unknown", 0.0))
                    else:
                        emotions_data.append(("unknown", 0.0))
                
                # Draw results
                frame = self.draw_results(frame, faces, emotions_data)
                
                # Add FPS counter
                frame_count += 1
                if frame_count % 30 == 0:  # Update FPS every 30 frames
                    fps_end_time = time.time()
                    fps = 30 / (fps_end_time - fps_start_time)
                    fps_start_time = fps_end_time
                
                cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Add face count
                cv2.putText(frame, f"Faces: {len(faces)}", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Show help text
                if show_help:
                    help_text = [
                        "Controls:",
                        "Q - Quit",
                        "S - Screenshot", 
                        "H - Toggle Help"
                    ]
                    for i, text in enumerate(help_text):
                        cv2.putText(frame, text, (10, frame.shape[0] - 80 + i*20), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                # Display frame
                cv2.imshow('Emotion Detection - Happy/Sad', frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("👋 Quitting...")
                    break
                elif key == ord('s'):
                    # Save screenshot
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    filename = f"emotion_detection_{timestamp}.jpg"
                    cv2.imwrite(filename, frame)
                    print(f"📸 Screenshot saved: {filename}")
                elif key == ord('h'):
                    show_help = not show_help
                    print(f"ℹ️  Help {'shown' if show_help else 'hidden'}")
        
        except KeyboardInterrupt:
            print("\n⚠️  Interrupted by user")
        
        finally:
            # Cleanup
            if cap:
                cap.release()
            cv2.destroyAllWindows()
            print("🔄 Camera released and windows closed")


def test_camera():
    """
    Simple camera test function to diagnose camera issues
    """
    print("� Testing camera access...")
    print("=" * 40)
    
    # Test different camera backends
    backends = [
        (cv2.CAP_DSHOW, "DirectShow (Windows)"),
        (cv2.CAP_MSMF, "Media Foundation (Windows)"),
        (cv2.CAP_ANY, "Any available backend")
    ]
    
    for backend_id, backend_name in backends:
        print(f"\n🧪 Testing {backend_name}...")
        
        for camera_id in range(3):  # Test cameras 0, 1, 2
            try:
                cap = cv2.VideoCapture(camera_id, backend_id)
                
                if cap.isOpened():
                    ret, frame = cap.read()
                    if ret and frame is not None:
                        print(f"✅ Camera {camera_id} works with {backend_name}")
                        print(f"   Resolution: {frame.shape[1]}x{frame.shape[0]}")
                        
                        # Show a test frame for 2 seconds
                        cv2.imshow(f'Camera Test - ID {camera_id}', frame)
                        cv2.waitKey(2000)
                        cv2.destroyAllWindows()
                        
                        cap.release()
                        return camera_id, backend_id  # Return working camera
                    else:
                        print(f"❌ Camera {camera_id} opened but can't read frames")
                else:
                    print(f"❌ Camera {camera_id} failed to open")
                
                cap.release()
                
            except Exception as e:
                print(f"❌ Camera {camera_id} error: {e}")
    
    print("\n❌ No working camera found!")
    print("\n🔧 Troubleshooting steps:")
    print("1. Check if camera is connected properly")
    print("2. Close other applications using the camera (Skype, Teams, etc.)")
    print("3. Check Windows Camera privacy settings:")
    print("   Settings > Privacy > Camera > Allow apps to access camera")
    print("4. Update camera drivers")
    print("5. Try running as administrator")
    print("6. Restart your computer")
    
    return None, None


def main():
    """
    Main function to run the emotion detector
    """
    print("🚀 Starting Emotion Detection System")
    print("=" * 50)
    
    # First test camera
    print("🔍 Testing camera compatibility...")
    working_camera, working_backend = test_camera()
    
    if working_camera is None:
        print("\n❌ Cannot proceed without a working camera!")
        return
    
    try:
        # Initialize detector with debug mode
        detector = EmotionDetector("best_model.pth", debug_mode=True)
        
        # Run detection with working camera
        print(f"\n🎥 Using camera {working_camera} with backend {working_backend}")
        detector.run_detection(camera_id=working_camera)
        
    except FileNotFoundError:
        print("❌ Error: Model file 'best_model.pth' not found!")
        print("💡 Make sure you have trained the model first using train.py")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    print("✅ Emotion detection completed!")


if __name__ == "__main__":
    main()