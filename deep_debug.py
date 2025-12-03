"""
Deep debug for webcam capture issue
"""
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import cv2
from deepface import DeepFace

print("="*60)
print("DEEP DEBUG - WEBCAM CAPTURE vs DATABASE")
print("="*60)

# Paths
webcam_img = "data/attendance_logs/temp_capture_2025-12-02.jpg"
db_img = "data/students/20220647/20220647_5.jpg"
db_path = "data/students"

if not os.path.exists(webcam_img):
    print(f"✗ Webcam image not found: {webcam_img}")
    exit(1)

print(f"\n📷 Webcam image: {webcam_img}")
print(f"📁 Database image: {db_img}")
print(f"📂 Database path: {db_path}")

# Test 1: Check image properties
print(f"\n{'='*60}")
print("TEST 1: IMAGE PROPERTIES")
print(f"{'='*60}")

for img_path, name in [(webcam_img, "Webcam"), (db_img, "Database")]:
    img = cv2.imread(img_path)
    if img is not None:
        h, w = img.shape[:2]
        size = os.path.getsize(img_path)
        print(f"\n{name}:")
        print(f"  Size: {w}x{h} pixels")
        print(f"  File size: {size/1024:.1f} KB")
        print(f"  Channels: {img.shape[2] if len(img.shape) > 2 else 1}")
    else:
        print(f"\n{name}: ✗ Cannot read image")

# Test 2: Face detection
print(f"\n{'='*60}")
print("TEST 2: FACE DETECTION")
print(f"{'='*60}")

for img_path, name in [(webcam_img, "Webcam"), (db_img, "Database")]:
    print(f"\n{name}:")
    try:
        faces = DeepFace.extract_faces(
            img_path=img_path,
            detector_backend='opencv',
            enforce_detection=False
        )
        print(f"  ✓ Detected {len(faces)} face(s)")
        for i, face in enumerate(faces):
            print(f"    Face {i+1}: confidence={face.get('confidence', 0):.2f}, "
                  f"region={face.get('facial_area', {})}")
    except Exception as e:
        print(f"  ✗ Error: {e}")

# Test 3: Direct comparison (verify)
print(f"\n{'='*60}")
print("TEST 3: DIRECT FACE VERIFICATION")
print(f"{'='*60}")

try:
    result = DeepFace.verify(
        img1_path=webcam_img,
        img2_path=db_img,
        model_name='Facenet512',
        detector_backend='opencv',
        enforce_detection=False
    )
    print(f"\nVerification result:")
    print(f"  Verified: {result['verified']}")
    print(f"  Distance: {result['distance']:.4f}")
    print(f"  Threshold: {result['threshold']:.4f}")
    print(f"  Model: {result['model']}")

    if result['distance'] < result['threshold']:
        print(f"  ✓ MATCH (distance < threshold)")
    else:
        print(f"  ✗ NO MATCH (distance >= threshold)")
        print(f"    Distance too high: {result['distance']:.4f} >= {result['threshold']:.4f}")

except Exception as e:
    print(f"✗ Error: {e}")

# Test 4: Find in database
print(f"\n{'='*60}")
print("TEST 4: FIND IN DATABASE")
print(f"{'='*60}")

try:
    print("\nSearching with Facenet512...")
    result = DeepFace.find(
        img_path=webcam_img,
        db_path=db_path,
        model_name='Facenet512',
        distance_metric='cosine',
        detector_backend='opencv',
        enforce_detection=False,
        silent=False  # Show progress
    )

    if result and len(result) > 0 and len(result[0]) > 0:
        print(f"\n✓ Found {len(result[0])} match(es)")
        print("\nTop 3 matches:")
        for idx, row in result[0].head(3).iterrows():
            print(f"\n  Match {idx+1}:")
            print(f"    Identity: {row['identity']}")
            print(f"    Distance: {row['distance']:.4f}")
            print(f"    Confidence: {(1-row['distance']):.2%}")
    else:
        print("\n✗ No matches found")
        print("\nPossible reasons:")
        print("  1. Face angle/expression too different")
        print("  2. Lighting conditions too different")
        print("  3. Image quality issue")
        print("  4. Need to re-register with more diverse samples")

except Exception as e:
    error_msg = str(e)
    print(f"\n✗ Error: {error_msg}")
    if "Length of values" in error_msg:
        print("\n  This means NO matching faces found in database")
        print("  The webcam image face doesn't match registered faces")

# Test 5: Visual comparison
print(f"\n{'='*60}")
print("TEST 5: RECOMMENDATIONS")
print(f"{'='*60}")

print("\n1. Check image quality:")
print("   - Open both images and compare visually")
print(f"   - Webcam: {webcam_img}")
print(f"   - Database: {db_img}")

print("\n2. If images look very different:")
print("   - Re-register student with more diverse angles")
print("   - Ensure good lighting when capturing")
print("   - Face should be 30-50% of frame size")

print("\n3. Try different model:")
print("   - ArcFace: Best for Asian faces (99% accuracy in test)")
print("   - Facenet: Good balance")
print("   - VGG-Face: Fastest but less accurate")

print("\n4. Adjust threshold:")
print("   - Current Facenet512 threshold: 0.45")
print("   - Can increase to 0.50 or 0.55 for easier matching")

print(f"\n{'='*60}")

