"""
Lớp View hiển thị thông tin cho người dùng (Mẫu thiết kế MVC)
View chịu trách nhiệm hiển thị dữ liệu và nhận input từ người dùng
"""
# Import các thư viện cần thiết
from typing import Dict, Any, List  # Type hints
from datetime import datetime  # Xử lý ngày giờ
from src.models.models import Student, AttendanceRecord  # Import các model


class ConsoleView:
    """Lớp View hiển thị thông tin trên Console/Terminal"""

    @staticmethod
    def display_menu():
        """Hiển thị menu chính"""
        print("\n" + "="*60)
        print("  FACE RECOGNITION ATTENDANCE SYSTEM")
        print("="*60)
        print("\n[STUDENT MANAGEMENT]")  # Quản lý sinh viên
        print("1. Register new student")
        print("2. Add face image to student")
        print("3. View student information")
        print("4. List all students")
        print("5. Update student information")
        print("6. Delete student")

        print("\n[ATTENDANCE]")  # Điểm danh
        print("7. Take attendance from image")
        print("8. Take attendance from webcam")
        print("9. View today's attendance")
        print("10. View attendance by date")
        print("11. View student attendance history")
        print("12. Generate attendance report")

        print("\n[SETTINGS]")  # Cài đặt
        print("13. Change recognition model")
        print("14. View available models")

        print("\n[OTHER]")  # Khác
        print("15. Test face recognition")
        print("0. Exit")
        print("="*60)

    @staticmethod
    def display_success(message: str):
        """Hiển thị thông báo thành công"""
        print(f"\n✓ SUCCESS: {message}")

    @staticmethod
    def display_error(message: str):
        """Hiển thị thông báo lỗi"""
        print(f"\n✗ ERROR: {message}")

    @staticmethod
    def display_info(message: str):
        """Hiển thị thông báo thông tin"""
        print(f"\nℹ INFO: {message}")

    @staticmethod
    def display_warning(message: str):
        """Hiển thị thông báo cảnh báo"""
        print(f"\n⚠ WARNING: {message}")

    @staticmethod
    def display_student(student: Student):
        """Hiển thị thông tin chi tiết một sinh viên"""
        print("\n" + "-"*60)
        print("STUDENT INFORMATION")
        print("-"*60)
        print(f"Student ID:   {student.student_id}")
        print(f"Full Name:    {student.full_name}")
        print(f"Class:        {student.class_name}")
        print(f"Email:        {student.email or 'N/A'}")
        print(f"Face Image:   {'Registered' if student.face_encoding_path else 'Not registered'}")
        print(f"Created:      {student.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print("-"*60)

    @staticmethod
    def display_students_list(students: List[Student]):
        """Hiển thị danh sách sinh viên dạng bảng"""
        if not students:
            print("\nNo students found.")
            return

        # In header bảng
        print("\n" + "="*100)
        print(f"{'ID':<15} {'Name':<25} {'Class':<15} {'Email':<25} {'Face':<10}")
        print("="*100)

        # In từng dòng sinh viên
        for student in students:
            face_status = "✓" if student.face_encoding_path else "✗"
            email = student.email[:22] + "..." if student.email and len(student.email) > 25 else (student.email or "N/A")
            print(f"{student.student_id:<15} {student.full_name:<25} {student.class_name:<15} {email:<25} {face_status:<10}")

        print("="*100)
        print(f"Total: {len(students)} student(s)")

    @staticmethod
    def display_attendance_record(record: AttendanceRecord):
        """Hiển thị một bản ghi điểm danh"""
        print("\n" + "-"*60)
        print("ATTENDANCE RECORD")
        print("-"*60)
        print(f"Student ID:   {record.student_id}")
        print(f"Date:         {record.session_date}")
        print(f"Check-in:     {record.check_in_time.strftime('%H:%M:%S')}")
        print(f"Status:       {record.status.upper()}")
        print(f"Confidence:   {record.confidence:.2%}" if record.confidence else "Confidence:   N/A")
        print(f"Model:        {record.model_used}")
        print(f"Notes:        {record.notes or 'N/A'}")
        print("-"*60)

    @staticmethod
    def display_attendance_list(records: List[AttendanceRecord], date: str = None):
        """Hiển thị danh sách bản ghi điểm danh"""
        if not records:
            print("\nNo attendance records found.")
            return

        title = f"ATTENDANCE RECORDS - {date}" if date else "ATTENDANCE RECORDS"
        print("\n" + "="*100)
        print(title)
        print("="*100)
        print(f"{'Student ID':<15} {'Check-in Time':<20} {'Status':<12} {'Confidence':<12} {'Model':<20}")
        print("="*100)

        for record in records:
            check_in = record.check_in_time.strftime('%Y-%m-%d %H:%M:%S')
            confidence = f"{record.confidence:.2%}" if record.confidence else "N/A"
            print(f"{record.student_id:<15} {check_in:<20} {record.status:<12} {confidence:<12} {record.model_used:<20}")

        print("="*100)
        print(f"Total: {len(records)} record(s)")

    @staticmethod
    def display_attendance_report(report: Dict[str, Any]):
        """Hiển thị báo cáo thống kê điểm danh"""
        print("\n" + "="*60)
        print(f"ATTENDANCE REPORT - {report['date']}")
        print("="*60)
        print(f"Total Records:  {report['total_records']}")
        print(f"Present:        {report['present']} ({report['present']/report['total_records']*100:.1f}%)" if report['total_records'] > 0 else "Present:        0")
        print(f"Late:           {report['late']}")
        print(f"Absent:         {report['absent']}")
        print("="*60)

    @staticmethod
    def display_recognition_result(result: Dict[str, Any]):
        """Hiển thị kết quả nhận diện khuôn mặt"""
        print("\n" + "-"*60)
        print("FACE RECOGNITION RESULT")
        print("-"*60)

        if result.get('recognized', False):
            # Nhận diện thành công
            rec_result = result['result']
            print(f"✓ RECOGNIZED")
            print(f"Student ID:   {rec_result.student_id}")
            print(f"Name:         {rec_result.student_name}")
            print(f"Confidence:   {rec_result.confidence:.2%}")
            print(f"Distance:     {rec_result.distance:.4f}")
            print(f"Model Used:   {rec_result.model_used}")
        else:
            # Không nhận diện được
            print(f"✗ NOT RECOGNIZED")
            if 'result' in result:
                rec_result = result['result']
                print(f"Model Used:   {rec_result.model_used}")

        print("-"*60)

    @staticmethod
    def display_models_list(models: List[str], current: str = None):
        """Hiển thị danh sách các mô hình nhận diện có sẵn"""
        print("\n" + "="*60)
        print("AVAILABLE FACE RECOGNITION MODELS")
        print("="*60)
        for i, model in enumerate(models, 1):
            marker = " (current)" if model == current else ""
            print(f"{i}. {model}{marker}")
        print("="*60)

    @staticmethod
    def get_input(prompt: str) -> str:
        """Lấy input từ người dùng"""
        return input(f"\n{prompt}: ").strip()

    @staticmethod
    def get_choice() -> str:
        """Lấy lựa chọn menu từ người dùng"""
        return input("\nEnter your choice: ").strip()

    @staticmethod
    def pause():
        """Tạm dừng và chờ người dùng nhấn Enter"""
        input("\nPress Enter to continue...")

    @staticmethod
    def clear_screen():
        """Xóa màn hình console"""
        import os
        os.system('clear' if os.name == 'posix' else 'cls')

