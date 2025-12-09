"""
Service layer for business logic
Tầng dịch vụ xử lý logic nghiệp vụ
- Điều phối các repository và strategy
- Xử lý các quy tắc nghiệp vụ phức tạp
"""
# Import các thư viện cần thiết
import os  # Thao tác với hệ điều hành (file, thư mục)
import shutil  # Copy, di chuyển file
from typing import List, Optional, Dict, Any  # Type hints
from datetime import datetime, date  # Xử lý ngày giờ
import cv2  # OpenCV để xử lý ảnh
import numpy as np  # Xử lý mảng số

# Import các thành phần nội bộ
from src.models.models import Student, AttendanceRecord, FaceRecognitionResult  # Các model
from src.repositories.repositories import StudentRepository, AttendanceRepository  # Các repository
from src.strategies.face_recognition_strategy import FaceRecognitionContext  # Context cho strategy pattern
from src.factories.factory import FaceRecognitionStrategyFactory  # Factory tạo strategy
from src.config.config import config  # Cấu hình ứng dụng


class StudentService:
    """
    Service for managing students
    Dịch vụ quản lý sinh viên
    - Xử lý đăng ký sinh viên mới
    - Quản lý ảnh khuôn mặt
    - CRUD sinh viên
    """

    def __init__(self):
        """Khởi tạo service với repository sinh viên"""
        self.repository = StudentRepository()

    def register_student(
        self,
        student_id: str,
        full_name: str,
        class_name: str,
        email: str = None,
        image_path: str = None,
        image_paths: List[str] = None
    ) -> Student:
        """
        Register a new student
        Đăng ký sinh viên mới

        Args:
            student_id: Mã sinh viên (duy nhất)
            full_name: Họ tên đầy đủ
            class_name: Tên lớp
            email: Email (tùy chọn)
            image_path: Đường dẫn ảnh khuôn mặt (tùy chọn, cho một ảnh)
            image_paths: Danh sách đường dẫn ảnh (tùy chọn, cho nhiều ảnh)

        Returns:
            Đối tượng Student đã được tạo
        """
        # Tạo thư mục riêng cho sinh viên để lưu ảnh
        student_dir = os.path.join(config.STUDENT_DATABASE_PATH, student_id)
        os.makedirs(student_dir, exist_ok=True)  # Tạo thư mục nếu chưa tồn tại

        face_encoding_path = None  # Đường dẫn đến ảnh khuôn mặt chính

        # Xử lý trường hợp có nhiều ảnh (phương pháp ưu tiên)
        if image_paths and len(image_paths) > 0:
            # Copy tất cả ảnh vào thư mục sinh viên
            for idx, img_path in enumerate(image_paths):
                if os.path.exists(img_path):
                    ext = os.path.splitext(img_path)[1]  # Lấy phần mở rộng file (.jpg, .png, etc.)
                    dest_path = os.path.join(student_dir, f"{student_id}_{idx}{ext}")  # Đặt tên file mới
                    shutil.copy(img_path, dest_path)  # Copy file ảnh
                    # Sử dụng ảnh đầu tiên làm ảnh chính
                    if idx == 0:
                        face_encoding_path = dest_path
        # Xử lý trường hợp một ảnh (tương thích ngược)
        elif image_path and os.path.exists(image_path):
            ext = os.path.splitext(image_path)[1]
            dest_path = os.path.join(student_dir, f"{student_id}_0{ext}")
            shutil.copy(image_path, dest_path)
            face_encoding_path = dest_path

        # Tạo đối tượng Student
        student = Student(
            student_id=student_id,
            full_name=full_name,
            class_name=class_name,
            email=email,
            face_encoding_path=face_encoding_path
        )

        # Lưu vào database thông qua repository
        return self.repository.create(student)

    def add_student_face_image(self, student_id: str, image_path: str = None, image_paths: List[str] = None) -> Student:
        """
        Add or update face image(s) for a student
        Thêm hoặc cập nhật ảnh khuôn mặt cho sinh viên

        Args:
            student_id: Mã sinh viên
            image_path: Đường dẫn một ảnh (tùy chọn)
            image_paths: Danh sách đường dẫn ảnh (tùy chọn)

        Returns:
            Đối tượng Student đã được cập nhật

        Raises:
            ValueError: Nếu không tìm thấy sinh viên hoặc không có ảnh hợp lệ
        """
        # Kiểm tra sinh viên tồn tại
        student = self.repository.get_by_id(student_id)
        if not student:
            raise ValueError(f"Student {student_id} not found")

        # Tạo thư mục nếu chưa có
        student_dir = os.path.join(config.STUDENT_DATABASE_PATH, student_id)
        os.makedirs(student_dir, exist_ok=True)

        face_encoding_path = None

        # Xử lý nhiều ảnh
        if image_paths and len(image_paths) > 0:
            for idx, img_path in enumerate(image_paths):
                if os.path.exists(img_path):
                    ext = os.path.splitext(img_path)[1]
                    dest_path = os.path.join(student_dir, f"{student_id}_{idx}{ext}")
                    shutil.copy(img_path, dest_path)
                    if idx == 0:
                        face_encoding_path = dest_path
        # Xử lý một ảnh
        elif image_path and os.path.exists(image_path):
            ext = os.path.splitext(image_path)[1]
            dest_path = os.path.join(student_dir, f"{student_id}_0{ext}")
            shutil.copy(image_path, dest_path)
            face_encoding_path = dest_path

        # Cập nhật đường dẫn ảnh nếu có
        if face_encoding_path:
            student.face_encoding_path = face_encoding_path
            return self.repository.update(student)

        raise ValueError("No valid image provided")

    def get_student(self, student_id: str) -> Optional[Student]:
        """
        Get student by ID
        Lấy sinh viên theo mã
        """
        return self.repository.get_by_id(student_id)

    def get_all_students(self) -> List[Student]:
        """
        Get all students
        Lấy tất cả sinh viên
        """
        return self.repository.get_all()

    def get_students_by_class(self, class_name: str) -> List[Student]:
        """
        Get all students in a specific class
        Lấy tất cả sinh viên trong một lớp cụ thể
        """
        return self.repository.get_by_class(class_name)

    def update_student(
        self,
        student_id: str,
        full_name: str = None,
        class_name: str = None,
        email: str = None
    ) -> Student:
        """
        Update student information
        Cập nhật thông tin sinh viên

        Chỉ cập nhật các trường được cung cấp (không None)
        """
        student = self.repository.get_by_id(student_id)
        if not student:
            raise ValueError(f"Student {student_id} not found")

        # Chỉ cập nhật nếu có giá trị mới
        if full_name:
            student.full_name = full_name
        if class_name:
            student.class_name = class_name
        if email:
            student.email = email

        return self.repository.update(student)

    def delete_student(self, student_id: str) -> bool:
        """
        Delete a student and their face data
        Xóa sinh viên và dữ liệu khuôn mặt của họ

        Returns:
            True nếu xóa thành công
        """
        student = self.repository.get_by_id(student_id)
        if not student:
            return False

        # Xóa thư mục chứa ảnh của sinh viên
        student_dir = os.path.join(config.STUDENT_DATABASE_PATH, student_id)
        if os.path.exists(student_dir):
            shutil.rmtree(student_dir)  # Xóa thư mục và tất cả nội dung bên trong

        # Xóa sinh viên khỏi database
        return self.repository.delete(student_id)


class AttendanceService:
    """
    Service for managing attendance
    Dịch vụ quản lý điểm danh
    - Đánh dấu điểm danh
    - Truy vấn lịch sử điểm danh
    - Tạo báo cáo
    """

    def __init__(self):
        """Khởi tạo service với các repository cần thiết"""
        self.repository = AttendanceRepository()  # Repository điểm danh
        self.student_repository = StudentRepository()  # Repository sinh viên

    def mark_attendance(
        self,
        student_id: str,
        confidence_score: float,
        model_used: str,
        status: str = 'present',
        notes: str = None
    ) -> AttendanceRecord:
        """
        Mark attendance for a student
        Đánh dấu điểm danh cho sinh viên

        Args:
            student_id: Mã sinh viên
            confidence_score: Điểm tin cậy của nhận diện (0.0 - 1.0)
            model_used: Tên model được sử dụng để nhận diện
            status: Trạng thái ('present', 'late', 'absent')
            notes: Ghi chú thêm

        Returns:
            AttendanceRecord đã được tạo

        Raises:
            ValueError: Nếu sinh viên không tồn tại hoặc đã điểm danh trong ngày
        """
        # Kiểm tra sinh viên có tồn tại không
        student = self.student_repository.get_by_id(student_id)
        if not student:
            raise ValueError(f"Student {student_id} not found")

        # Kiểm tra đã điểm danh trong ngày chưa
        today = date.today().strftime("%Y-%m-%d")  # Lấy ngày hôm nay (định dạng YYYY-MM-DD)
        existing = self.repository.get_by_student_and_date(student_id, today)

        if existing:
            # Đã điểm danh rồi, không cho điểm danh lại
            raise ValueError(f"Attendance already marked for student {student_id} today")

        # Tạo bản ghi điểm danh mới
        attendance = AttendanceRecord(
            student_id=student_id,
            check_in_time=datetime.now(),  # Thời gian hiện tại
            confidence=confidence_score,
            model_used=model_used,
            status=status,
            session_date=today,
            notes=notes
        )

        # Lưu vào database
        return self.repository.create(attendance)

    def get_attendance_by_student(self, student_id: str) -> List[AttendanceRecord]:
        """
        Get all attendance records for a student
        Lấy tất cả bản ghi điểm danh của một sinh viên
        """
        return self.repository.get_by_student(student_id)

    def get_attendance_by_date(self, session_date: str) -> List[AttendanceRecord]:
        """
        Get all attendance records for a specific date
        Lấy tất cả bản ghi điểm danh của một ngày cụ thể
        """
        return self.repository.get_by_date(session_date)

    def get_today_attendance(self) -> List[AttendanceRecord]:
        """
        Get today's attendance records
        Lấy bản ghi điểm danh của ngày hôm nay
        """
        today = date.today().strftime("%Y-%m-%d")
        return self.repository.get_by_date(today)

    def update_attendance_status(self, record_id: int, status: str, notes: str = None) -> AttendanceRecord:
        """
        Update attendance status
        Cập nhật trạng thái điểm danh

        Args:
            record_id: ID của bản ghi cần cập nhật
            status: Trạng thái mới
            notes: Ghi chú mới (tùy chọn)
        """
        record = self.repository.get_by_id(record_id)
        if not record:
            raise ValueError(f"Attendance record {record_id} not found")

        record.status = status
        if notes:
            record.notes = notes

        return self.repository.update(record)

    def generate_attendance_report(self, session_date: str = None) -> Dict[str, Any]:
        """
        Generate attendance report
        Tạo báo cáo điểm danh

        Args:
            session_date: Ngày cần tạo báo cáo (mặc định: hôm nay)

        Returns:
            Dictionary chứa thống kê điểm danh:
            - date: Ngày
            - total_records: Tổng số bản ghi
            - present: Số sinh viên có mặt
            - late: Số sinh viên đi trễ
            - absent: Số sinh viên vắng
            - records: Danh sách các bản ghi
        """
        # Mặc định lấy ngày hôm nay
        if session_date is None:
            session_date = date.today().strftime("%Y-%m-%d")

        # Lấy tất cả bản ghi trong ngày
        records = self.repository.get_by_date(session_date)

        # Đếm số lượng theo từng trạng thái
        total_present = sum(1 for r in records if r.status == 'present')
        total_late = sum(1 for r in records if r.status == 'late')
        total_absent = sum(1 for r in records if r.status == 'absent')

        return {
            'date': session_date,
            'total_records': len(records),
            'present': total_present,
            'late': total_late,
            'absent': total_absent,
            'records': records
        }


class FaceRecognitionService:
    """
    Service for face recognition operations
    Dịch vụ nhận diện khuôn mặt
    - Sử dụng Strategy Pattern để hỗ trợ nhiều model khác nhau
    - Tích hợp với DeepFace library
    """

    def __init__(self, model_name: str = None):
        """
        Khởi tạo service với model được chỉ định

        Args:
            model_name: Tên model (mặc định lấy từ config)
        """
        # Sử dụng model mặc định nếu không chỉ định
        if model_name is None:
            model_name = config.DEFAULT_MODEL

        # Tạo strategy cho model được chọn thông qua Factory
        strategy = FaceRecognitionStrategyFactory.create_strategy(model_name)
        # Tạo context để sử dụng strategy
        self.context = FaceRecognitionContext(strategy)
        # Repository để truy vấn thông tin sinh viên
        self.student_repository = StudentRepository()

    def change_model(self, model_name: str):
        """
        Change the recognition model
        Thay đổi model nhận diện

        Args:
            model_name: Tên model mới (VGG-Face, ArcFace, Facenet, etc.)
        """
        strategy = FaceRecognitionStrategyFactory.create_strategy(model_name)
        self.context.strategy = strategy

    def recognize_student(self, image_path: str) -> FaceRecognitionResult:
        """
        Recognize student from image
        Nhận diện sinh viên từ ảnh

        Args:
            image_path: Đường dẫn đến ảnh chứa khuôn mặt

        Returns:
            FaceRecognitionResult chứa kết quả nhận diện
        """
        try:
            # Kiểm tra database có ảnh không
            if not self._validate_database_has_images():
                return FaceRecognitionResult(
                    success=False,
                    student_id=None,
                    student_name=None,
                    confidence=0.0,
                    distance=1.0,
                    model_used=self.context.get_model_name(),
                    error_message="No students with face images found in database. Please register students first.",
                    face_detected=True
                )

            # Thực hiện nhận diện khuôn mặt bằng DeepFace
            results = self.context.recognize_face(
                image_path=image_path,
                database_path=config.STUDENT_DATABASE_PATH
            )

            # Lấy thông tin model và ngưỡng
            model_name = self.context.get_model_name()
            threshold = config.get_threshold(model_name)

            # In thông tin debug
            print(f"\n🔍 Recognition Debug:")
            print(f"   Model: {model_name}")
            print(f"   Threshold: {threshold}")
            print(f"   Results found: {len(results) if results else 0}")

            # Kiểm tra có kết quả không
            if results and len(results) > 0 and len(results[0]) > 0:
                # Lấy kết quả tốt nhất (khoảng cách nhỏ nhất)
                best_match = results[0].iloc[0]
                distance = best_match['distance']  # Khoảng cách giữa các vector đặc trưng
                confidence = 1 - distance  # Độ tin cậy = 1 - khoảng cách

                print(f"   Best match distance: {distance:.4f}")
                print(f"   Confidence: {confidence:.2%}")

                # Trích xuất student_id từ đường dẫn ảnh
                identity_path = best_match['identity']
                matched_student_id = self._extract_student_id_from_path(identity_path)

                print(f"   Matched ID: {matched_student_id}")

                # KIỂM TRA NGHIÊM NGẶT: Cả khoảng cách VÀ độ tin cậy tối thiểu
                if distance < threshold and confidence >= config.MIN_CONFIDENCE_FOR_ATTENDANCE:
                    print(f"   ✓ PASS: Distance < {threshold:.4f} AND Confidence >= {config.MIN_CONFIDENCE_FOR_ATTENDANCE:.0%}")

                    if matched_student_id:
                        # Lấy thông tin sinh viên từ database
                        student = self.student_repository.get_by_id(matched_student_id)

                        if student:
                            # Validation bổ sung: Kiểm tra tính nhất quán của top 3 kết quả
                            if len(results[0]) > 1:
                                top_matches = results[0].head(3)
                                print(f"   📊 Top 3 matches:")
                                for idx, row in top_matches.iterrows():
                                    match_id = self._extract_student_id_from_path(row['identity'])
                                    match_conf = 1 - row['distance']
                                    print(f"      {idx+1}. {match_id}: {match_conf:.2%} (dist: {row['distance']:.4f})")

                            # Trả về kết quả thành công
                            return FaceRecognitionResult(
                                success=True,
                                student_id=student.student_id,
                                student_name=student.full_name,
                                confidence=confidence,
                                distance=distance,
                                model_used=model_name,
                                face_detected=True
                            )
                else:
                    # Kết quả không đạt ngưỡng
                    print(f"   ✗ REJECT: Match failed validation!")
                    if distance >= threshold:
                        print(f"      - Distance {distance:.4f} >= threshold {threshold:.4f}")
                    if confidence < config.MIN_CONFIDENCE_FOR_ATTENDANCE:
                        print(f"      - Confidence {confidence:.2%} < minimum {config.MIN_CONFIDENCE_FOR_ATTENDANCE:.0%}")
                    print(f"   💡 Tips:")
                    print(f"      - Register student with MORE high-quality images")
                    print(f"      - Try different model (ArcFace recommended: best accuracy)")
                    print(f"      - Ensure good lighting and face angle")
            else:
                # Không tìm thấy kết quả khớp
                print(f"   ✗ No faces detected in database match")
                print(f"   Possible causes:")
                print(f"     - Webcam image quality different from registered images")
                print(f"     - Face angle/expression too different")
                print(f"     - Try switching model (ArcFace works best: 99% accuracy)")
                print(f"     - Consider re-registering with webcam images")

            # Không tìm thấy kết quả khớp
            return FaceRecognitionResult(
                success=False,
                student_id=None,
                student_name=None,
                confidence=0.0,
                distance=1.0,
                model_used=model_name,
                face_detected=True
            )

        except Exception as e:
            # Xử lý lỗi
            print(f"Error in face recognition: {str(e)}")
            return FaceRecognitionResult(
                success=False,
                student_id=None,
                student_name=None,
                confidence=0.0,
                distance=1.0,
                model_used=self.context.get_model_name(),
                error_message=str(e),
                face_detected=True
            )

    def _extract_student_id_from_path(self, path: str) -> Optional[str]:
        """
        Extract student ID from file path
        Trích xuất mã sinh viên từ đường dẫn file

        Đường dẫn có dạng: data/students/STUDENT_ID/STUDENT_ID.ext
        """
        # Chuẩn hóa đường dẫn (xử lý cả / và \)
        normalized_path = path.replace('\\', '/')
        parts = normalized_path.split('/')

        # Tìm phần "students" và lấy thư mục tiếp theo
        for i, part in enumerate(parts):
            if part == 'students' and i + 1 < len(parts):
                student_id = parts[i + 1]
                print(f"   Extracted student_id: {student_id}")
                return student_id

        # Fallback: thử trích xuất từ tên file
        filename = os.path.basename(path)
        if '_' in filename:
            student_id = filename.split('_')[0]
            print(f"   Extracted student_id from filename: {student_id}")
            return student_id

        return None

    def _validate_database_has_images(self) -> bool:
        """
        Validate that database has at least one student with images
        Kiểm tra database có ít nhất một sinh viên có ảnh không
        Đồng thời in cảnh báo cho sinh viên không có ảnh

        Returns:
            True nếu có ít nhất một sinh viên có ảnh, False nếu không
        """
        students_path = config.STUDENT_DATABASE_PATH
        if not os.path.exists(students_path):
            return False

        has_images = False
        students_without_images = []

        # Duyệt qua từng thư mục sinh viên
        for student_id in os.listdir(students_path):
            student_dir = os.path.join(students_path, student_id)

            # Bỏ qua nếu không phải thư mục
            if not os.path.isdir(student_dir):
                continue

            # Đếm số file ảnh
            image_files = [f for f in os.listdir(student_dir)
                          if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]

            if len(image_files) == 0:
                students_without_images.append(student_id)
            else:
                has_images = True

        # In cảnh báo cho sinh viên không có ảnh
        if students_without_images:
            print(f"\n⚠️  WARNING: Students without face images:")
            for sid in students_without_images:
                print(f"   - {sid} (0 images) - Cannot be recognized!")
            print(f"   Please add images for these students using option 2 in menu.\n")

        return has_images

    def verify_student(self, image_path: str, student_id: str) -> Dict[str, Any]:
        """
        Verify if image matches a specific student
        Xác minh ảnh có khớp với sinh viên cụ thể không

        Args:
            image_path: Đường dẫn ảnh cần xác minh
            student_id: Mã sinh viên cần so sánh

        Returns:
            Dictionary chứa kết quả xác minh
        """
        # Lấy thông tin sinh viên
        student = self.student_repository.get_by_id(student_id)
        if not student or not student.face_encoding_path:
            return {
                'verified': False,
                'message': 'Student not found or no face image registered'
            }

        try:
            # Thực hiện xác minh khuôn mặt
            result = self.context.verify_face(image_path, student.face_encoding_path)
            return result
        except Exception as e:
            return {
                'verified': False,
                'message': f'Error: {str(e)}'
            }

    def get_available_models(self) -> List[str]:
        """
        Get list of available recognition models
        Lấy danh sách các model nhận diện có sẵn
        """
        return FaceRecognitionStrategyFactory.get_available_models()
