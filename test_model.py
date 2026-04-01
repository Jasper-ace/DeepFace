import torch
import torch.nn as nn
from torchvision import models, transforms
import cv2
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

class ModelTester:
    def __init__(self, model_path="best_model.pth"):
        self.device = torch.device("cpu")
        self.model = self._load_model(model_path)
        
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        
        # Face detection
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
    def _load_model(self, model_path):
        """Load the trained model"""
        model = models.resnet18(weights=None)
        model.fc = nn.Linear(model.fc.in_features, 2)
        model.load_state_dict(torch.load(model_path, map_location=self.device))
        model.eval()
        return model
    
    def test_model_behavior(self):
        """Test the model with different inputs to understand its behavior"""
        print("🧪 Testing Model Behavior")
        print("=" * 30)
        
        # Test with random noise
        print("1. Testing with random noise:")
        for i in range(5):
            random_input = torch.randn(1, 3, 224, 224)
            with torch.no_grad():
                outputs = self.model(random_input)
                probs = torch.nn.functional.softmax(outputs, dim=1)
                print(f"   Random {i+1}: sad={probs[0][0]:.3f}, happy={probs[0][1]:.3f}")
        
        # Test with solid colors
        print("\n2. Testing with solid colors:")
        colors = [
            ("Black", [0, 0, 0]),
            ("White", [255, 255, 255]),
            ("Red", [255, 0, 0]),
            ("Green", [0, 255, 0]),
            ("Blue", [0, 0, 255])
        ]
        
        for color_name, rgb in colors:
            # Create solid color image
            color_image = np.full((224, 224, 3), rgb, dtype=np.uint8)
            input_tensor = self.transform(color_image).unsqueeze(0)
            
            with torch.no_grad():
                outputs = self.model(input_tensor)
                probs = torch.nn.functional.softmax(outputs, dim=1)
                print(f"   {color_name}: sad={probs[0][0]:.3f}, happy={probs[0][1]:.3f}")
    
    def test_with_camera(self):
        """Test model with live camera input"""
        print("\n🎥 Testing with Camera")
        print("=" * 25)
        print("Instructions:")
        print("- Press 'h' for happy test")
        print("- Press 's' for sad test")
        print("- Press 'q' to quit")
        
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        
        if not cap.isOpened():
            print("❌ Could not open camera")
            return
        
        test_results = {'happy_tests': [], 'sad_tests': []}
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame = cv2.flip(frame, 1)
                
                # Detect faces
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(50, 50))
                
                for (x, y, w, h) in faces:
                    # Extract face
                    face_roi = frame[y:y+h, x:x+w]
                    
                    # Predict emotion
                    input_tensor = self.transform(face_roi).unsqueeze(0)
                    
                    with torch.no_grad():
                        outputs = self.model(input_tensor)
                        probs = torch.nn.functional.softmax(outputs, dim=1)
                        sad_prob = probs[0][0].item()
                        happy_prob = probs[0][1].item()
                    
                    # Draw results
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    
                    # Show probabilities
                    cv2.putText(frame, f"Sad: {sad_prob:.3f}", (x, y-40), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    cv2.putText(frame, f"Happy: {happy_prob:.3f}", (x, y-20), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                
                # Show instructions
                cv2.putText(frame, "H=Happy test, S=Sad test, Q=Quit", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                cv2.imshow('Model Testing', frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('h') and len(faces) > 0:
                    # Record happy test
                    face_roi = frame[faces[0][1]:faces[0][1]+faces[0][3], 
                                   faces[0][0]:faces[0][0]+faces[0][2]]
                    input_tensor = self.transform(face_roi).unsqueeze(0)
                    
                    with torch.no_grad():
                        outputs = self.model(input_tensor)
                        probs = torch.nn.functional.softmax(outputs, dim=1)
                        test_results['happy_tests'].append({
                            'sad': probs[0][0].item(),
                            'happy': probs[0][1].item()
                        })
                    
                    print(f"✅ Happy test recorded: sad={probs[0][0]:.3f}, happy={probs[0][1]:.3f}")
                    
                elif key == ord('s') and len(faces) > 0:
                    # Record sad test
                    face_roi = frame[faces[0][1]:faces[0][1]+faces[0][3], 
                                   faces[0][0]:faces[0][0]+faces[0][2]]
                    input_tensor = self.transform(face_roi).unsqueeze(0)
                    
                    with torch.no_grad():
                        outputs = self.model(input_tensor)
                        probs = torch.nn.functional.softmax(outputs, dim=1)
                        test_results['sad_tests'].append({
                            'sad': probs[0][0].item(),
                            'happy': probs[0][1].item()
                        })
                    
                    print(f"✅ Sad test recorded: sad={probs[0][0]:.3f}, happy={probs[0][1]:.3f}")
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
        
        # Analyze results
        self._analyze_test_results(test_results)
    
    def _analyze_test_results(self, results):
        """Analyze the test results"""
        print("\n📊 Test Results Analysis")
        print("=" * 25)
        
        if results['happy_tests']:
            print(f"\n😊 Happy Expression Tests ({len(results['happy_tests'])} samples):")
            happy_sad_avg = np.mean([r['sad'] for r in results['happy_tests']])
            happy_happy_avg = np.mean([r['happy'] for r in results['happy_tests']])
            print(f"   Average sad probability: {happy_sad_avg:.3f}")
            print(f"   Average happy probability: {happy_happy_avg:.3f}")
            
            correct_happy = sum(1 for r in results['happy_tests'] if r['happy'] > r['sad'])
            print(f"   Correctly classified as happy: {correct_happy}/{len(results['happy_tests'])}")
        
        if results['sad_tests']:
            print(f"\n😢 Sad Expression Tests ({len(results['sad_tests'])} samples):")
            sad_sad_avg = np.mean([r['sad'] for r in results['sad_tests']])
            sad_happy_avg = np.mean([r['happy'] for r in results['sad_tests']])
            print(f"   Average sad probability: {sad_sad_avg:.3f}")
            print(f"   Average happy probability: {sad_happy_avg:.3f}")
            
            correct_sad = sum(1 for r in results['sad_tests'] if r['sad'] > r['happy'])
            print(f"   Correctly classified as sad: {correct_sad}/{len(results['sad_tests'])}")
        
        print("\n🔍 Diagnosis:")
        if results['happy_tests'] and results['sad_tests']:
            # Check if model is biased
            all_happy_probs = [r['happy'] for r in results['happy_tests'] + results['sad_tests']]
            all_sad_probs = [r['sad'] for r in results['happy_tests'] + results['sad_tests']]
            
            avg_happy = np.mean(all_happy_probs)
            avg_sad = np.mean(all_sad_probs)
            
            if avg_happy > 0.7:
                print("⚠️  Model seems biased towards HAPPY predictions")
                print("💡 Suggestion: The model might need retraining with more balanced data")
            elif avg_sad > 0.7:
                print("⚠️  Model seems biased towards SAD predictions")
                print("💡 Suggestion: The model might need retraining with more balanced data")
            else:
                print("✅ Model seems reasonably balanced")
        
        print("\n🔧 Recommendations:")
        print("1. If model is always predicting one class, retrain with more balanced data")
        print("2. If predictions are swapped, check class order in detect.py")
        print("3. If model is uncertain, try collecting more training data")
        print("4. Consider data augmentation during training")

def main():
    print("🧪 Model Testing and Diagnosis Tool")
    print("=" * 40)
    
    try:
        tester = ModelTester("best_model.pth")
        
        # Test model behavior
        tester.test_model_behavior()
        
        # Test with camera
        print("\n" + "=" * 40)
        response = input("Do you want to test with camera? (y/n): ")
        if response.lower() == 'y':
            tester.test_with_camera()
    
    except FileNotFoundError:
        print("❌ Model file 'best_model.pth' not found!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()