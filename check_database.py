# -*- coding: utf-8 -*-
"""
Utility script to check student database status
Shows which students have images and which don't
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config.config import config


def check_student_database():
    """Check and report status of all students in database"""

    print("=" * 60)
    print("📊 STUDENT DATABASE STATUS REPORT")
    print("=" * 60)

    students_path = config.STUDENT_DATABASE_PATH

    if not os.path.exists(students_path):
        print(f"❌ Student database path not found: {students_path}")
        return

    # Get all student directories
    student_dirs = [d for d in os.listdir(students_path)
                   if os.path.isdir(os.path.join(students_path, d))]

    if not student_dirs:
        print("⚠️  No students found in database!")
        return

    print(f"\nTotal students registered: {len(student_dirs)}\n")

    students_with_images = []
    students_without_images = []

    # Check each student
    for student_id in sorted(student_dirs):
        student_dir = os.path.join(students_path, student_id)

        # Count image files
        image_files = [f for f in os.listdir(student_dir)
                      if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]

        # Count original vs augmented
        original_images = [f for f in image_files if not f.startswith('aug_')]
        augmented_images = [f for f in image_files if f.startswith('aug_')]

        if len(image_files) > 0:
            students_with_images.append({
                'id': student_id,
                'total': len(image_files),
                'original': len(original_images),
                'augmented': len(augmented_images)
            })
        else:
            students_without_images.append(student_id)

    # Report students WITH images
    if students_with_images:
        print("✅ STUDENTS WITH IMAGES (Can be recognized):")
        print("-" * 60)
        for student in students_with_images:
            status = "✓ GOOD" if student['original'] >= 5 else "⚠ FEW"
            print(f"   {status} | {student['id']:<15} | "
                  f"Total: {student['total']:3d} | "
                  f"Original: {student['original']:2d} | "
                  f"Aug: {student['augmented']:3d}")
        print()

    # Report students WITHOUT images
    if students_without_images:
        print("❌ STUDENTS WITHOUT IMAGES (Cannot be recognized):")
        print("-" * 60)
        for student_id in students_without_images:
            print(f"   ✗ {student_id:<15} | 0 images | ⚠️  ADD IMAGES REQUIRED!")
        print()
        print("⚠️  WARNING: These students CANNOT be recognized!")
        print("   Use Menu Option 2 to add face images.")
        print()

    # Summary
    print("=" * 60)
    print("SUMMARY:")
    print(f"   ✅ Students ready for recognition: {len(students_with_images)}")
    print(f"   ❌ Students needing images: {len(students_without_images)}")

    if students_without_images:
        print(f"\n   ⚠️  ACTION REQUIRED: Add images for {len(students_without_images)} student(s)")
    else:
        print(f"\n   ✓ All students have images!")

    print("=" * 60)

    # Check for cached models
    print("\n🔍 CHECKING CACHED MODELS:")
    print("-" * 60)
    pkl_files = [f for f in os.listdir(students_path) if f.endswith('.pkl')]

    if pkl_files:
        print(f"   Found {len(pkl_files)} cached model file(s):")
        for pkl in pkl_files:
            pkl_path = os.path.join(students_path, pkl)
            size_mb = os.path.getsize(pkl_path) / (1024 * 1024)
            print(f"   - {pkl} ({size_mb:.2f} MB)")
        print(f"\n   💡 TIP: If recognition is inaccurate, delete cache:")
        print(f"       Remove-Item \"{students_path}\\*.pkl\" -Force")
    else:
        print(f"   ✓ No cached models (will be generated on first recognition)")

    print("=" * 60)


if __name__ == "__main__":
    try:
        check_student_database()
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

