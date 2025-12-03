"""
Test and debug face recognition
"""
import os
import sys
from deepface import DeepFace
import cv2

print("="*60)
print("FACE RECOGNITION DEBUG TOOL")
print("="*60)

# Check database
db_path = "data/students"
if not os.path.exists(db_path):
    print(f"✗ Database path not found: {db_path}")
    sys.exit(1)

# Count images in database
image_count = 0
student_folders = []
for root, dirs, files in os.walk(db_path):
    for file in files:
        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
            image_count += 1
    if root != db_path and dirs == []:  # Leaf folder
        student_folders.append(os.path.basename(root))

print(f"\n✓ Database path: {db_path}")
print(f"✓ Total images: {image_count}")
print(f"✓ Student folders: {len(set(student_folders))}")
if student_folders:
    print(f"  Students: {', '.join(set(student_folders))}")

if image_count == 0:
    print("\n✗ ERROR: No images found in database!")
    print("  Please register students first using option 1 in main menu")
    sys.exit(1)

# Test image path
test_image = input("\n📷 Enter path to test image (or press Enter to skip): ").strip()

if test_image and os.path.exists(test_image):
    print(f"\n{'='*60}")
    print("TESTING IMAGE")
    print(f"{'='*60}")

    # Test 1: OpenCV face detection
    print("\n[1/3] Testing OpenCV face detection...")
    try:
        img = cv2.imread(test_image)
        if img is None:
            print("✗ Cannot read image")
        else:
            cascade_path = os.path.join('data', 'models', 'haarcascade_frontalface_default.xml')
            if not os.path.exists(cascade_path):
                cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'

            face_cascade = cv2.CascadeClassifier(cascade_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            print(f"✓ Detected {len(faces)} face(s) using Haar Cascade")
            if len(faces) == 0:
                print("  ⚠ Warning: No faces detected by OpenCV")
            elif len(faces) > 1:
                print(f"  ⚠ Warning: Multiple faces detected ({len(faces)})")
    except Exception as e:
        print(f"✗ Error: {e}")

    # Test 2: DeepFace detection
    print("\n[2/3] Testing DeepFace face detection...")
    try:
        # Try with enforce_detection=False first
        result = DeepFace.extract_faces(
            img_path=test_image,
            detector_backend='opencv',
            enforce_detection=False
        )
        print(f"✓ DeepFace detected {len(result)} face(s)")
        for i, face in enumerate(result):
            print(f"  Face {i+1}: confidence={face.get('confidence', 0):.2f}")
    except Exception as e:
        print(f"✗ Error: {e}")

    # Test 3: Recognition against database
    print("\n[3/3] Testing face recognition against database...")
    print("  Using model: VGG-Face")
    print("  Using backend: opencv")
    print("  Using enforce_detection: False")

    try:
        result = DeepFace.find(
            img_path=test_image,
            db_path=db_path,
            model_name='VGG-Face',
            distance_metric='cosine',
            detector_backend='opencv',
            enforce_detection=False,
            silent=False
        )

        if result and len(result) > 0 and len(result[0]) > 0:
            print(f"\n✓ Found {len(result[0])} potential match(es)")
            print("\nTop 3 matches:")
            for idx, row in result[0].head(3).iterrows():
                identity = row['identity']
                distance = row['distance']
                confidence = 1 - distance
                print(f"  {idx+1}. {os.path.basename(os.path.dirname(identity))}")
                print(f"     Distance: {distance:.4f}, Confidence: {confidence:.2%}")
        else:
            print("✗ No matches found in database")
            print("  Possible reasons:")
            print("  - Face in test image doesn't match any registered students")
            print("  - Distance threshold too strict")
            print("  - Poor image quality")

    except Exception as e:
        print(f"✗ Error during recognition: {e}")
        if "Length of values" in str(e):
            print("  This error usually means no matching faces found")
            print("  Suggestions:")
            print("  - Make sure registered student images are clear")
            print("  - Try registering with more sample images (10+)")
            print("  - Ensure test image has good lighting and face is visible")

else:
    print("\n⊘ Skipping image test")

print(f"\n{'='*60}")
print("DEBUG COMPLETE")
print(f"{'='*60}")
print("\nNext steps:")
print("1. If no images in database: Register students first")
print("2. If detection fails: Check image quality and lighting")
print("3. If no matches: Register more sample images per student")
print("4. Try different models: Facenet, Facenet512, ArcFace")

