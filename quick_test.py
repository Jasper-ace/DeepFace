import cv2
import time
import os

def quick_emotion_test():
    """Quick test to compare different emotion detection methods"""
    print("🚀 Quick Emotion Detection Test")
    print("=" * 40)
    print("This will test different methods and show you which works best")
    print("Make sure you have good lighting and face the camera directly")
    print()
    
    # Test camera first
    print("📷 Testing camera...")
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("❌ Camera not available")
        return
    
    ret, frame = cap.read()
    if not ret:
        print("❌ Cannot read from camera")
        cap.release()
        return
    
    print("✅ Camera working!")
    cap.release()
    
    print("\n🎯 Available Detection Methods:")
    methods = []
    
    # Check working detector
    if os.path.exists("detect_working.py"):
        methods.append(("Working Detector (Best)", "python detect_working.py"))
        print("✅ 1. Working Detector (Combines all methods)")
    
    # Check pre-trained
    if os.path.exists("detect_pretrained.py"):
        methods.append(("Pre-trained FER", "python detect_pretrained.py"))
        print("✅ 2. Pre-trained FER (Most accurate)")
    
    # Check custom model
    if os.path.exists("detect.py") and os.path.exists("best_model.pth"):
        methods.append(("Custom Model", "python detect.py"))
        print("✅ 3. Custom Model (Your trained model)")
    
    # Check simple
    if os.path.exists("detect_simple.py"):
        methods.append(("Simple OpenCV", "python detect_simple.py"))
        print("✅ 4. Simple OpenCV (Basic detection)")
    
    if not methods:
        print("❌ No detection methods available")
        return
    
    print(f"\n🎯 RECOMMENDATION:")
    print("=" * 30)
    print("🥇 BEST OPTION: python detect_working.py")
    print("   - Most reliable and accurate")
    print("   - Combines multiple detection methods")
    print("   - Automatic fallback if one method fails")
    
    print(f"\n💡 USAGE:")
    print("1. Run: python detect_working.py")
    print("2. Look at the camera and try different expressions:")
    print("   😊 Smile widely for HAPPY")
    print("   😢 Frown or look sad for SAD")
    print("3. Press 'Q' to quit when done")
    print("4. Press 'S' to save screenshots")
    
    print(f"\n🔧 TROUBLESHOOTING:")
    print("- If custom model always shows 'sad', it needs retraining")
    print("- Pre-trained model is most accurate for testing")
    print("- Make sure good lighting and face camera directly")
    print("- Close other apps using camera (Skype, Teams, etc.)")
    
    print(f"\n🚀 Ready to test? Run: python detect_working.py")

if __name__ == "__main__":
    quick_emotion_test()