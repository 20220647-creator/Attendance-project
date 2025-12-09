# -*- coding: utf-8 -*-
"""
Utility script to check student database status
Script tiện ích để kiểm tra trạng thái cơ sở dữ liệu sinh viên
- Hiển thị sinh viên nào có ảnh và sinh viên nào không có
- Kiểm tra các file cache model
"""
# Import các thư viện cần thiết
import os  # Thao tác với file/thư mục
import sys  # Thao tác với hệ thống

# Thêm thư mục gốc của project vào path để import được các module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import cấu hình ứng dụng
from src.config.config import config


def check_student_database():
    """
    Check and report status of all students in database
    Kiểm tra và báo cáo trạng thái của tất cả sinh viên trong database
    """

    # In tiêu đề báo cáo
    print("=" * 60)
    print("📊 STUDENT DATABASE STATUS REPORT")
    print("=" * 60)

    # Lấy đường dẫn thư mục chứa dữ liệu sinh viên
    students_path = config.STUDENT_DATABASE_PATH

    # Kiểm tra thư mục có tồn tại không
    if not os.path.exists(students_path):
        print(f"❌ Student database path not found: {students_path}")
        return

    # Lấy danh sách các thư mục con (mỗi thư mục = 1 sinh viên)
    student_dirs = [d for d in os.listdir(students_path)
                   if os.path.isdir(os.path.join(students_path, d))]

    # Kiểm tra có sinh viên nào không
    if not student_dirs:
        print("⚠️  No students found in database!")
        return

    # In tổng số sinh viên
    print(f"\nTotal students registered: {len(student_dirs)}\n")

    # Danh sách để phân loại sinh viên
    students_with_images = []  # Sinh viên có ảnh
    students_without_images = []  # Sinh viên không có ảnh

    # Duyệt qua từng thư mục sinh viên
    for student_id in sorted(student_dirs):
        student_dir = os.path.join(students_path, student_id)

        # Đếm số file ảnh (các định dạng phổ biến)
        image_files = [f for f in os.listdir(student_dir)
                      if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]

        # Phân loại ảnh gốc và ảnh đã augment
        original_images = [f for f in image_files if not f.startswith('aug_')]  # Ảnh gốc
        augmented_images = [f for f in image_files if f.startswith('aug_')]  # Ảnh đã tăng cường

        # Phân loại sinh viên dựa trên số ảnh
        if len(image_files) > 0:
            students_with_images.append({
                'id': student_id,
                'total': len(image_files),
                'original': len(original_images),
                'augmented': len(augmented_images)
            })
        else:
            students_without_images.append(student_id)

    # Báo cáo sinh viên CÓ ảnh
    if students_with_images:
        print("✅ STUDENTS WITH IMAGES (Can be recognized):")
        print("-" * 60)
        for student in students_with_images:
            # Đánh giá trạng thái: GOOD nếu >= 5 ảnh gốc, FEW nếu ít hơn
            status = "✓ GOOD" if student['original'] >= 5 else "⚠ FEW"
            print(f"   {status} | {student['id']:<15} | "
                  f"Total: {student['total']:3d} | "
                  f"Original: {student['original']:2d} | "
                  f"Aug: {student['augmented']:3d}")
        print()

    # Báo cáo sinh viên KHÔNG có ảnh
    if students_without_images:
        print("❌ STUDENTS WITHOUT IMAGES (Cannot be recognized):")
        print("-" * 60)
        for student_id in students_without_images:
            print(f"   ✗ {student_id:<15} | 0 images | ⚠️  ADD IMAGES REQUIRED!")
        print()
        print("⚠️  WARNING: These students CANNOT be recognized!")
        print("   Use Menu Option 2 to add face images.")
        print()

    # Tổng kết
    print("=" * 60)
    print("SUMMARY:")
    print(f"   ✅ Students ready for recognition: {len(students_with_images)}")
    print(f"   ❌ Students needing images: {len(students_without_images)}")

    # Hiển thị cảnh báo nếu có sinh viên cần thêm ảnh
    if students_without_images:
        print(f"\n   ⚠️  ACTION REQUIRED: Add images for {len(students_without_images)} student(s)")
    else:
        print(f"\n   ✓ All students have images!")

    print("=" * 60)

    # Kiểm tra các file model đã cache
    print("\n🔍 CHECKING CACHED MODELS:")
    print("-" * 60)

    # Tìm các file .pkl (file cache của DeepFace)
    pkl_files = [f for f in os.listdir(students_path) if f.endswith('.pkl')]

    if pkl_files:
        # Có file cache
        print(f"   Found {len(pkl_files)} cached model file(s):")
        for pkl in pkl_files:
            pkl_path = os.path.join(students_path, pkl)
            size_mb = os.path.getsize(pkl_path) / (1024 * 1024)  # Chuyển sang MB
            print(f"   - {pkl} ({size_mb:.2f} MB)")
        print(f"\n   💡 TIP: If recognition is inaccurate, delete cache:")
        print(f"       Remove-Item \"{students_path}\\*.pkl\" -Force")
    else:
        # Không có file cache
        print(f"   ✓ No cached models (will be generated on first recognition)")

    print("=" * 60)


# Điểm bắt đầu khi chạy trực tiếp script
if __name__ == "__main__":
    try:
        check_student_database()  # Chạy hàm kiểm tra
    except Exception as e:
        # Xử lý lỗi và in traceback
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
