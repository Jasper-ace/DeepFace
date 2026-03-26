import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import numpy as np

def load_model(model_path="best_model.pth"):
    """Load the trained model"""
    # Create model architecture
    model = models.resnet18(weights=None)
    model.fc = nn.Linear(model.fc.in_features, 2)  # 2 classes: happy/sad
    
    # Load weights
    model.load_state_dict(torch.load(model_path, map_location='cpu'))
    model.eval()
    
    return model

def test_class_mapping():
    """Test different class mappings to find the correct one"""
    
    print("🔍 Testing Class Mapping")
    print("=" * 30)
    
    # Load model
    model = load_model()
    
    # Image preprocessing
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    
    # Test different class orders
    class_mappings = [
        ['happy', 'sad'],
        ['sad', 'happy']
    ]
    
    print("📝 Instructions:")
    print("1. Look at your face in a mirror")
    print("2. Make a CLEAR HAPPY expression (big smile)")
    print("3. Check which mapping gives 'happy' as the result")
    print("4. Then make a CLEAR SAD expression (frown)")
    print("5. Check which mapping gives 'sad' as the result")
    print()
    
    # Create a test image (you can replace this with actual face image)
    print("⚠️  Note: This is a template. For accurate testing:")
    print("1. Save a clear photo of your happy face as 'test_happy.jpg'")
    print("2. Save a clear photo of your sad face as 'test_sad.jpg'")
    print("3. Run this script again")
    print()
    
    # Test with dummy data to show the concept
    dummy_input = torch.randn(1, 3, 224, 224)
    
    with torch.no_grad():
        outputs = model(dummy_input)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        predicted_class = torch.argmax(probabilities, dim=1).item()
    
    print("🧪 Model Output Analysis:")
    print(f"Raw outputs: {outputs.cpu().numpy()}")
    print(f"Probabilities: {probabilities.cpu().numpy()}")
    print(f"Predicted class index: {predicted_class}")
    print()
    
    for i, mapping in enumerate(class_mappings):
        print(f"Mapping {i+1}: {mapping}")
        print(f"  Index 0 → {mapping[0]}")
        print(f"  Index 1 → {mapping[1]}")
        print(f"  Predicted: {mapping[predicted_class]}")
        print()
    
    return class_mappings

def check_training_data_structure():
    """Check how the training data was organized"""
    
    print("📁 Training Data Structure Check")
    print("=" * 35)
    
    import os
    
    data_dir = "datasets"
    
    if os.path.exists(data_dir):
        print(f"✅ Found datasets directory: {data_dir}")
        
        for split in ['train', 'val', 'test']:
            split_path = os.path.join(data_dir, split)
            if os.path.exists(split_path):
                print(f"\n📂 {split.upper()} folder:")
                
                classes = sorted(os.listdir(split_path))
                for i, class_name in enumerate(classes):
                    class_path = os.path.join(split_path, class_name)
                    if os.path.isdir(class_path):
                        count = len([f for f in os.listdir(class_path) 
                                   if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
                        print(f"  Index {i}: {class_name} ({count} images)")
                
                print(f"\n🎯 Class order in training: {classes}")
                return classes
    else:
        print(f"❌ Datasets directory not found: {data_dir}")
        print("💡 The class order depends on how your training data was organized")
    
    return None

def main():
    print("🔍 Class Mapping Verification Tool")
    print("=" * 40)
    
    # Check training data structure
    training_classes = check_training_data_structure()
    
    print("\n" + "=" * 40)
    
    # Test class mapping
    test_mappings = test_class_mapping()
    
    print("=" * 40)
    print("📋 RECOMMENDATIONS:")
    print()
    
    if training_classes:
        print(f"✅ Based on training data structure:")
        print(f"   Correct class order: {training_classes}")
        print(f"   Use: self.class_names = {training_classes}")
    else:
        print("⚠️  Could not determine from training data")
    
    print("\n🧪 To verify experimentally:")
    print("1. Run detect.py with debug mode")
    print("2. Make a clear HAPPY face")
    print("3. Check if it says 'happy' or 'sad'")
    print("4. If wrong, swap the class order in detect.py")
    
    print("\n🔧 In detect.py, try these options:")
    print("   Option 1: self.class_names = ['happy', 'sad']")
    print("   Option 2: self.class_names = ['sad', 'happy']")
    
    print("\n✅ The correct one is whichever matches your actual expression!")

if __name__ == "__main__":
    main()