import cv2
import os
import time

def test_camera():
    """Test camera functionality"""
    print("🧪 Testing camera access...")
    
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("❌ Camera failed to open")
        return False
    
    ret, frame = cap.read()
    if not ret:
        print("❌ Could not read frame")
        cap.release()
        return False
    
    print("✅ Camera working!")
    print(f"   Resolution: {frame.shape[1]}x{frame.shape[0]}")
    
    cap.release()
    return True

def test_detectors():
    """Test all available emotion detectors"""
    print("\n🔍 Testing emotion detectors...")
    
    detectors = []
    
    # Test 1: Working detector (recommended)
    try:
        from detect_working import WorkingEmotionDetector
        detector = WorkingEmotionDetector("best_model.pth")
        detectors.append(("Working Detector (Recommended)", "detect_working.py"))
        print("✅ Working detector available")
    except Exception as e:
        print(f"❌ Working detector failed: {e}")
    
    # Test 2: Pre-trained FER
    try:
        from detect_pretrained import PretrainedEmotionDetector
        detector = PretrainedEmotionDetector()
        detectors.append(("Pre-trained FER", "detect_pretrained.py"))
        print("✅ Pre-trained FER available")
    except Exception as e:
        print(f"❌ Pre-trained FER failed: {e}")
    
    # Test 3: Custom model
    if os.path.exists("best_model.pth"):
        try:
            from detect import EmotionDetector
            detector = EmotionDetector("best_model.pth")
            detectors.append(("Custom Model", "detect.py"))
            print("✅ Custom model available")
        except Exception as e:
            print(f"❌ Custom model failed: {e}")
    else:
        print("⚠️  Custom model file (best_model.pth) not found")
    
    # Test 4: Simple OpenCV
    try:
        from detect_simple import SimpleEmotionDetector
        detector = SimpleEmotionDetector()
        detectors.append(("Simple OpenCV", "detect_simple.py"))
        print("✅ Simple OpenCV available")
    except Exception as e:
        print(f"❌ Simple OpenCV failed: {e}")
    
    return detectors

def main():
    print("🚀 Emotion Detection System Test")
    print("=" * 50)
    
    # Test camera first
    if not test_camera():
        print("\n❌ Camera test failed! Fix camera issues first.")
        return
    
    # Test detectors
    available_detectors = test_detectors()
    
    if not available_detectors:
        print("\n❌ No working detectors found!")
        return
    
    print(f"\n✅ Found {len(available_detectors)} working detector(s):")
    for i, (name, filename) in enumerate(available_detectors, 1):
        print(f"   {i}. {name} ({filename})")
    
    print("\n🎯 RECOMMENDATIONS:")
    print("=" * 30)
    
    if any("Working Detector" in name for name, _ in available_detectors):
        print("🥇 BEST: Run 'python detect_working.py'")
        print("   - Combines multiple methods for best accuracy")
        print("   - Automatic fallback if one method fails")
        print("   - Most reliable option")
    
    elif any("Pre-trained FER" in name for name, _ in available_detectors):
        print("🥈 GOOD: Run 'python detect_pretrained.py'")
        print("   - Uses professional pre-trained model")
        print("   - High accuracy for emotion detection")
    
    elif any("Custom Model" in name for name, _ in available_detectors):
        print("🥉 OK: Run 'python detect.py'")
        print("   - Uses your trained model")
        print("   - May need fine-tuning for better accuracy")
    
    else:
        print("🔧 BASIC: Run 'python detect_simple.py'")
        print("   - Simple OpenCV-based detection")
        print("   - Limited accuracy but always works")
    
    print("\n💡 USAGE TIPS:")
    print("- Press 'Q' to quit any detector")
    print("- Press 'S' to save screenshots")
    print("- Make sure good lighting for best results")
    print("- Face the camera directly")
    
    print("\n🔧 If you have issues:")
    print("1. Close other apps using camera (Skype, Teams, etc.)")
    print("2. Check Windows camera privacy settings")
    print("3. Try running as administrator")
    print("4. Restart your computer if needed")

if __name__ == "__main__":
    main()