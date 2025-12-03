"""
Test all face recognition models
"""
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from src.services.services import FaceRecognitionService
from src.config.config import config

print("="*60)
print("TEST ALL MODELS")
print("="*60)

# Use student's own image for testing
test_image = "data/students/20220647/20220647_5.jpg"

if not os.path.exists(test_image):
    print("✗ Test image not found")
    exit(1)

print(f"Test image: {test_image}\n")

models = ['VGG-Face', 'Facenet', 'Facenet512', 'ArcFace']

for model_name in models:
    print(f"\n{'='*60}")
    print(f"TESTING: {model_name}")
    print(f"{'='*60}")

    try:
        service = FaceRecognitionService(model_name=model_name)
        result = service.recognize_student(test_image)

        if result.success:
            print(f"✓ SUCCESS")
            print(f"  Student: {result.student_id} - {result.student_name}")
            print(f"  Confidence: {result.confidence:.2%}")
            print(f"  Distance: {result.distance:.4f}")
            print(f"  Threshold: {config.get_threshold(model_name):.4f}")
        else:
            print(f"✗ FAILED")
            print(f"  Error: {result.error_message or 'No match found'}")

    except Exception as e:
        print(f"✗ ERROR: {e}")

print(f"\n{'='*60}")
print("TEST COMPLETE")
print(f"{'='*60}")

