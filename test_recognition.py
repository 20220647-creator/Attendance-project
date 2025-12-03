"""
Quick test for face recognition
"""
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow warnings

from src.services.services import FaceRecognitionService
from src.config.config import config

print("="*60)
print("QUICK FACE RECOGNITION TEST")
print("="*60)

# Check if student images exist
student_dir = "data/students/20220647"
if os.path.exists(student_dir):
    images = [f for f in os.listdir(student_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
    print(f"\n✓ Found {len(images)} registered images for student 20220647")
else:
    print("\n✗ Student 20220647 not found in database")
    exit(1)

# Get test image
test_image = input("\nEnter path to test image (or press Enter to use first student image): ").strip()

if not test_image:
    # Use one of the student images as test
    test_image = os.path.join(student_dir, images[5])  # Use 6th image
    print(f"Using: {test_image}")

if not os.path.exists(test_image):
    print(f"✗ Image not found: {test_image}")
    exit(1)

print(f"\n{'='*60}")
print("TESTING RECOGNITION")
print(f"{'='*60}")

# Test recognition
service = FaceRecognitionService()
result = service.recognize_student(test_image)

print(f"\n{'='*60}")
print("RESULT")
print(f"{'='*60}")
print(f"Success: {result.success}")
if result.success:
    print(f"Student ID: {result.student_id}")
    print(f"Student Name: {result.student_name}")
    print(f"Confidence: {result.confidence:.2%}")
    print(f"Distance: {result.distance:.4f}")
else:
    print(f"Error: {result.error_message or 'No match found'}")

print(f"\n{'='*60}")

