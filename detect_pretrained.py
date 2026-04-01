import cv2
import numpy as np
from fer.fer import FER
import time

class PretrainedEmotionDetector:
    def __init__(self):
        """
        Initialize with pre-trained FER (Facial Emotion Recognition) model
        """
        print("🚀 Loading pre-trained emotion detection model...")
        
        # Initialize FER detector
        self.detector = FER(mtcnn=True)  # Uses MTCNN for better face detection
        
        # Colors for visualization
        self.colors = {
            'happy': (0, 255, 0),      # Green
            'sad': (0, 0, 255),        # Red
            'neutral': (255, 255, 0),  # Cyan
            'angry': (0, 0, 255),      # Red
            'fear': (255, 0, 255),     # Magenta
            'disgust': (0, 128, 255),  # Orange
            'surprise': (255, 255, 0)  # Yellow
        }
        
        print("✅ Pre-trained model loaded successfully!")
        print("🎯 Detects: Happy, Sad, Angry, Fear, Disgust, Surprise, Neutral")
    
    def detect_emotions(self, frame):
        """
        Detect emotions in frame using pre-trained model
        """
        try:
            # Detect emotions
            result = self.detector.detect_emotions(frame)
            
            emotions_data = []
            for face_data in result:
                # Get bounding box
                box = face_data['box']
                x, y, w, h = box
                
                # Get emotions with confidence scores
                emotions = face_data['emotions']
                
                # Find dominant emotion
                dominant_emotion = max(emotions, key=emotions.get)
                confidence = emotions[dominant_emotion]
                
                # Focus on happy/sad for your use case
                happy_score = emotions.get('happy', 0)
                sad_score = emotions.get('sad', 0)
                
                # Determine primary emotion (happy/sad focus)
                if happy_score > sad_score and happy_score > 0.3:
                    primary_emotion = 'happy'
                    primary_confidence = happy_score
                elif sad_score > happy_score and sad_score > 0.3:
                    primary_emotion = 'sad'
                    primary_confidence = sad_score
                else:
                    primary_emotion = 'neutral'
                    primary_confidence = emotions.get('neutral', 0)
                
                emotions_data.append({
                    'box': (x, y, w, h),
                    'primary_emotion': primary_emotion,
                    'primary_confidence': primary_confidence,
                    'all_emotions': emotions,
                    'dominant_emotion': dominant_emotion,
                    'dominant_confidence': confidence
                })
            
            return emotions_data
            
        except Exception as e:
            print(f"❌ Error in emotion detection: {e}")
            return []
    
    def draw_results(self, frame, emotions_data):
        """
        Draw emotion detection results on frame
        """
        for data in emotions_data:
            x, y, w, h = data['box']
            primary_emotion = data['primary_emotion']
            primary_confidence = data['primary_confidence']
            all_emotions = data['all_emotions']
            
            # Get color for primary emotion
            color = self.colors.get(primary_emotion, (255, 255, 255))
            
            # Draw bounding box
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            
            # Draw primary emotion label
            label = f"{primary_emotion.upper()}: {primary_confidence:.2f}"
            
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
            
            # Draw detailed emotions on the side
            y_offset = y + h + 20
            for emotion, score in all_emotions.items():
                if score > 0.1:  # Only show emotions with >10% confidence
                    emotion_text = f"{emotion}: {score:.2f}"
                    cv2.putText(
                        frame, 
                        emotion_text, 
                        (x, y_offset), 
                        cv2.FONT_HERSHEY_SIMPLEX, 
                        0.4, 
                        (255, 255, 255), 
                        1
                    )
                    y_offset += 15
            
            # Add emoji
            if primary_emotion == 'happy':
                cv2.putText(frame, "😊", (x + w - 30, y + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            elif primary_emotion == 'sad':
                cv2.putText(frame, "😢", (x + w - 30, y + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
            elif primary_emotion == 'neutral':
                cv2.putText(frame, "😐", (x + w - 30, y + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        
        return frame
    
    def run_detection(self, camera_id=0):
        """
        Run real-time emotion detection
        """
        print("🎥 Starting camera...")
        print("📋 Instructions:")
        print("   - Press 'q' to quit")
        print("   - Press 's' to save screenshot")
        print("=" * 50)
        
        # Initialize camera
        cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)
        
        if not cap.isOpened():
            print("❌ Error: Could not open camera")
            return
        
        # Set camera properties
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        frame_count = 0
        fps_start_time = time.time()
        fps = 0.0  # Initialize FPS variable
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("❌ Error: Could not read frame")
                    break
                
                # Flip frame for mirror effect
                frame = cv2.flip(frame, 1)
                
                # Detect emotions
                emotions_data = self.detect_emotions(frame)
                
                # Draw results
                frame = self.draw_results(frame, emotions_data)
                
                # Add FPS counter
                frame_count += 1
                if frame_count % 30 == 0:
                    fps_end_time = time.time()
                    fps = 30 / (fps_end_time - fps_start_time)
                    fps_start_time = fps_end_time
                
                cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Add face count
                cv2.putText(frame, f"Faces: {len(emotions_data)}", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Display frame
                cv2.imshow('Pre-trained Emotion Detection', frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("👋 Quitting...")
                    break
                elif key == ord('s'):
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    filename = f"emotion_pretrained_{timestamp}.jpg"
                    cv2.imwrite(filename, frame)
                    print(f"📸 Screenshot saved: {filename}")
        
        except KeyboardInterrupt:
            print("\n⚠️ Interrupted by user")
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
            print("🔄 Camera released")


def main():
    print("🚀 Pre-trained Emotion Detection System")
    print("=" * 45)
    
    try:
        detector = PretrainedEmotionDetector()
        detector.run_detection(camera_id=0)
        
    except ImportError:
        print("❌ Error: Required packages not installed!")
        print("💡 Install with: pip install fer tensorflow opencv-python")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("✅ Detection completed!")


if __name__ == "__main__":
    main()