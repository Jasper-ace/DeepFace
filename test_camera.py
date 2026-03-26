import cv2
import sys

def test_all_cameras():
    """
    Test all available cameras and backends
    """
    print("🔍 Testing all available cameras...")
    print("=" * 50)
    
    # Test different backends
    backends = [
        (cv2.CAP_DSHOW, "DirectShow (Windows)"),
        (cv2.CAP_MSMF, "Media Foundation (Windows)"), 
        (cv2.CAP_ANY, "Any Backend"),
        (cv2.CAP_V4L2, "Video4Linux (if available)")
    ]
    
    working_cameras = []
    
    for backend_id, backend_name in backends:
        print(f"\n🧪 Testing {backend_name}...")
        
        for camera_id in range(5):  # Test cameras 0-4
            try:
                print(f"   Trying camera {camera_id}...", end=" ")
                
                cap = cv2.VideoCapture(camera_id, backend_id)
                
                if cap.isOpened():
                    # Try to read a frame
                    ret, frame = cap.read()
                    
                    if ret and frame is not None:
                        height, width = frame.shape[:2]
                        print(f"✅ WORKS! Resolution: {width}x{height}")
                        working_cameras.append((camera_id, backend_id, backend_name, width, height))
                        
                        # Show preview for 1 second
                        cv2.imshow(f'Camera {camera_id} - {backend_name}', frame)
                        cv2.waitKey(1000)
                        cv2.destroyAllWindows()
                    else:
                        print("❌ Opens but no frames")
                else:
                    print("❌ Won't open")
                
                cap.release()
                
            except Exception as e:
                print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("📊 SUMMARY:")
    
    if working_cameras:
        print("✅ Working cameras found:")
        for cam_id, backend_id, backend_name, width, height in working_cameras:
            print(f"   Camera {cam_id}: {backend_name} ({width}x{height})")
        
        # Test the first working camera
        print(f"\n🎥 Testing first working camera (ID {working_cameras[0][0]})...")
        test_camera_live(working_cameras[0][0], working_cameras[0][1])
    else:
        print("❌ No working cameras found!")
        print_troubleshooting_tips()

def test_camera_live(camera_id, backend_id):
    """
    Test a specific camera with live preview
    """
    print(f"🎬 Starting live preview for camera {camera_id}")
    print("Press 'q' to quit, 's' to save screenshot")
    
    cap = cv2.VideoCapture(camera_id, backend_id)
    
    if not cap.isOpened():
        print("❌ Failed to open camera for live test")
        return
    
    frame_count = 0
    
    try:
        while True:
            ret, frame = cap.read()
            
            if not ret:
                print("❌ Failed to read frame")
                break
            
            frame_count += 1
            
            # Add frame counter
            cv2.putText(frame, f"Frame: {frame_count}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Add instructions
            cv2.putText(frame, "Press 'q' to quit, 's' to save", (10, frame.shape[0] - 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            cv2.imshow('Camera Test - Live Preview', frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                filename = f"camera_test_{camera_id}.jpg"
                cv2.imwrite(filename, frame)
                print(f"📸 Screenshot saved: {filename}")
    
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("✅ Camera test completed")

def print_troubleshooting_tips():
    """
    Print troubleshooting tips for camera issues
    """
    print("\n🔧 TROUBLESHOOTING TIPS:")
    print("=" * 30)
    print("1. 📷 Check physical connection:")
    print("   - USB camera: Try different USB ports")
    print("   - Built-in camera: Check if enabled in BIOS")
    
    print("\n2. 🔒 Check Windows permissions:")
    print("   - Go to Settings > Privacy & Security > Camera")
    print("   - Enable 'Allow apps to access your camera'")
    print("   - Enable 'Allow desktop apps to access your camera'")
    
    print("\n3. 📱 Close other applications:")
    print("   - Skype, Teams, Zoom, OBS, etc.")
    print("   - Windows Camera app")
    print("   - Any other video software")
    
    print("\n4. 🔄 Update drivers:")
    print("   - Device Manager > Cameras > Update driver")
    print("   - Or download from manufacturer website")
    
    print("\n5. 🛠️ Try these commands:")
    print("   - Run as Administrator")
    print("   - Restart Windows")
    print("   - Check Device Manager for errors")
    
    print("\n6. 🧪 Test with Windows Camera app:")
    print("   - Open Windows Camera app first")
    print("   - If it works there, the camera is functional")

def quick_test():
    """
    Quick test for the most common camera setup
    """
    print("⚡ Quick Camera Test")
    print("=" * 20)
    
    # Try the most common setup first
    try:
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print("✅ Camera 0 with DirectShow works!")
                cv2.imshow('Quick Test', frame)
                cv2.waitKey(2000)
                cv2.destroyAllWindows()
                cap.release()
                return True
        
        cap.release()
    except:
        pass
    
    print("❌ Quick test failed, running full test...")
    return False

if __name__ == "__main__":
    print("🎥 Camera Testing Utility")
    print("=" * 30)
    
    # Quick test first
    if not quick_test():
        # Full test if quick test fails
        test_all_cameras()
    
    print("\n✅ Testing completed!")