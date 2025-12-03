"""
Compare all models with latest webcam capture
"""
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from src.services.services import FaceRecognitionService
from src.config.config import config
from datetime import date

print("="*60)
print("COMPARE ALL MODELS WITH WEBCAM IMAGE")
print("="*60)

# Find latest temp capture
temp_path = os.path.join('data', 'attendance_logs', f'temp_capture_{date.today()}.jpg')

if not os.path.exists(temp_path):
    print(f"\nNo webcam capture found at: {temp_path}")
    print("Please capture an image first using option 8 in main menu")
    exit(1)

print(f"\nWebcam image: {temp_path}")
print(f"File exists: True")

# Get file size
size_kb = os.path.getsize(temp_path) / 1024
print(f"File size: {size_kb:.1f} KB")

models = ['VGG-Face', 'Facenet', 'Facenet512', 'ArcFace']

print(f"\n{'='*60}")
print("TESTING ALL MODELS")
print(f"{'='*60}")

results = []

for model_name in models:
    print(f"\n[{model_name}]")
    try:
        service = FaceRecognitionService(model_name=model_name)
        result = service.recognize_student(temp_path)

        results.append({
            'model': model_name,
            'success': result.success,
            'student_id': result.student_id,
            'confidence': result.confidence,
            'distance': result.distance
        })

        if result.success:
            print(f"SUCCESS: {result.student_id} ({result.confidence:.2%})")
        else:
            print(f"FAILED: No match")

    except Exception as e:
        print(f"ERROR: {e}")
        results.append({
            'model': model_name,
            'success': False,
            'error': str(e)
        })

# Summary
print(f"\n{'='*60}")
print("SUMMARY")
print(f"{'='*60}")

print(f"\n{'Model':<15} {'Status':<10} {'Confidence':<12} {'Distance':<10}")
print("-"*60)

for r in results:
    status = "OK" if r['success'] else "FAIL"
    conf = f"{r.get('confidence', 0):.2%}" if r['success'] else "N/A"
    dist = f"{r.get('distance', 0):.4f}" if r['success'] else "N/A"
    print(f"{r['model']:<15} {status:<10} {conf:<12} {dist:<10}")

success_count = sum(1 for r in results if r['success'])
print(f"\nSuccess rate: {success_count}/{len(results)} models")

if success_count == 0:
    print(f"\nRECOMMENDATIONS:")
    print("1. Re-register student with WEBCAM images (not file upload)")
    print("2. Ensure good lighting when capturing")
    print("3. Face should fill 30-50% of frame")
    print("4. Look straight at camera")
    print("5. Try ArcFace model (best for Asian faces)")
elif success_count < len(results):
    print(f"\nSome models failed. This is normal - use working models.")
else:
    print(f"\nAll models working! System ready.")

print(f"\n{'='*60}")

