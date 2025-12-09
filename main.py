"""
Điểm khởi động chính của ứng dụng
Hệ thống điểm danh nhận diện khuôn mặt
"""
# Import các thư viện cần thiết
import os  # Xử lý file và thư mục
import sys  # Truy cập các tham số hệ thống
from datetime import date  # Xử lý ngày tháng

# Import các controller để xử lý logic
from src.controllers.controllers import StudentController, AttendanceController, FaceRecognitionController
# Import view để hiển thị giao diện
from src.views.views import ConsoleView
# Import các tiện ích
from src.utils.utils import CameraUtility, ImageValidator
# Import cấu hình
from src.config.config import config


class AttendanceApplication:
    """Lớp ứng dụng chính điều khiển toàn bộ hệ thống"""

    def __init__(self):
        """Khởi tạo ứng dụng với các controller và view"""
        self.student_controller = StudentController()  # Controller quản lý sinh viên
        self.attendance_controller = AttendanceController()  # Controller quản lý điểm danh
        self.face_controller = FaceRecognitionController()  # Controller nhận diện khuôn mặt
        self.view = ConsoleView()  # View hiển thị console
        self.running = True  # Biến trạng thái chạy ứng dụng
        self.current_model = config.DEFAULT_MODEL  # Mô hình nhận diện hiện tại

    def run(self):
        """Chạy vòng lặp chính của ứng dụng"""
        # Hiển thị thông tin khởi tạo
        self.view.display_info(f"System initialized with model: {self.current_model}")

        # Vòng lặp chính
        while self.running:
            try:
                # Hiển thị menu
                self.view.display_menu()
                # Lấy lựa chọn từ người dùng
                choice = self.view.get_choice()

                # Xử lý lựa chọn
                self.handle_choice(choice)

            except KeyboardInterrupt:
                # Xử lý khi người dùng nhấn Ctrl+C
                print("\n\nInterrupted by user")
                self.running = False
            except Exception as e:
                # Bắt các lỗi không mong muốn
                self.view.display_error(f"Unexpected error: {str(e)}")
                self.view.pause()

        # Hiển thị lời chào tạm biệt
        print("\n" + "="*60)
        print("Thank you for using Face Recognition Attendance System!")
        print("="*60 + "\n")

    def handle_choice(self, choice: str):
        """
        Xử lý lựa chọn menu của người dùng

        Args:
            choice: Chuỗi lựa chọn từ người dùng
        """
        # Dictionary ánh xạ lựa chọn đến phương thức xử lý
        handlers = {
            '1': self.register_student,  # Đăng ký sinh viên
            '2': self.add_face_image,  # Thêm ảnh khuôn mặt
            '3': self.view_student,  # Xem thông tin sinh viên
            '4': self.list_students,  # Liệt kê sinh viên
            '5': self.update_student,  # Cập nhật sinh viên
            '6': self.delete_student,  # Xóa sinh viên
            '7': self.take_attendance_image,  # Điểm danh từ ảnh
            '8': self.take_attendance_webcam,  # Điểm danh từ webcam
            '9': self.view_today_attendance,  # Xem điểm danh hôm nay
            '10': self.view_attendance_by_date,  # Xem điểm danh theo ngày
            '11': self.view_student_history,  # Xem lịch sử sinh viên
            '12': self.generate_report,  # Tạo báo cáo
            '13': self.change_model,  # Thay đổi mô hình
            '14': self.view_models,  # Xem danh sách mô hình
            '15': self.test_recognition,  # Kiểm tra nhận diện
            '0': self.exit_application  # Thoát ứng dụng
        }

        # Lấy hàm xử lý tương ứng
        handler = handlers.get(choice)
        if handler:
            handler()  # Gọi hàm xử lý
        else:
            # Lựa chọn không hợp lệ
            self.view.display_error("Invalid choice. Please try again.")
            self.view.pause()

    def register_student(self):
        """Đăng ký sinh viên mới"""
        print("\n" + "="*60)
        print("REGISTER NEW STUDENT")
        print("="*60)

        # Lấy thông tin sinh viên từ người dùng
        student_id = self.view.get_input("Enter Student ID")
        if not student_id:
            self.view.display_error("Student ID cannot be empty")
            self.view.pause()
            return

        full_name = self.view.get_input("Enter Full Name")
        if not full_name:
            self.view.display_error("Full name cannot be empty")
            self.view.pause()
            return

        class_name = self.view.get_input("Enter Class Name")
        email = self.view.get_input("Enter Email (optional)")

        # Hỏi có muốn thêm ảnh khuôn mặt không
        image_choice = self.view.get_input("Add face images now? (y/n)").lower()
        image_paths = None

        if image_choice == 'y':
            img_choice = self.view.get_input("1. From file  2. From webcam (multiple samples) (1/2)")

            if img_choice == '1':
                # Single file mode (backward compatibility)
                image_path = self.view.get_input("Enter image file path")
                if image_path and os.path.exists(image_path):
                    is_valid, message = ImageValidator.validate_face_image(image_path)
                    if is_valid:
                        image_paths = [image_path]
                    else:
                        self.view.display_error(message)

            elif img_choice == '2':
                # Multiple samples from webcam (NEW!)
                self.view.display_info(f"Will capture {config.NUM_FACE_SAMPLES} face samples for better recognition")
                self.view.display_info("This improves accuracy by capturing different angles and expressions")

                student_dir = os.path.join(config.STUDENT_DATABASE_PATH, student_id)
                image_paths = CameraUtility.capture_multiple_from_webcam(
                    save_dir=student_dir,
                    student_id=student_id,
                    num_samples=config.NUM_FACE_SAMPLES,
                    delay=config.SAMPLE_CAPTURE_DELAY
                )

                if not image_paths:
                    self.view.display_warning("No images captured")

        result = self.student_controller.register_new_student(
            student_id=student_id,
            full_name=full_name,
            class_name=class_name,
            email=email if email else None,
            image_paths=image_paths
        )

        if result['success']:
            self.view.display_success(result['message'])
            self.view.display_student(result['student'])
        else:
            self.view.display_error(result['message'])

        self.view.pause()

    def add_face_image(self):
        """Add face image to existing student"""
        print("\n" + "="*60)
        print("ADD FACE IMAGE")
        print("="*60)

        student_id = self.view.get_input("Enter Student ID")

        img_choice = self.view.get_input("1. From file  2. From webcam (multiple samples) (1/2)")

        image_paths = None
        if img_choice == '1':
            # Single file mode
            image_path = self.view.get_input("Enter image file path")
            if image_path and os.path.exists(image_path):
                is_valid, message = ImageValidator.validate_face_image(image_path)
                if is_valid:
                    image_paths = [image_path]
                else:
                    self.view.display_error(message)
                    self.view.pause()
                    return

        elif img_choice == '2':
            # Multiple samples from webcam
            self.view.display_info(f"Will capture {config.NUM_FACE_SAMPLES} face samples for better recognition")

            student_dir = os.path.join(config.STUDENT_DATABASE_PATH, student_id)
            image_paths = CameraUtility.capture_multiple_from_webcam(
                save_dir=student_dir,
                student_id=student_id,
                num_samples=config.NUM_FACE_SAMPLES,
                delay=config.SAMPLE_CAPTURE_DELAY
            )

        if image_paths:
            result = self.student_controller.add_face_image(student_id, image_paths=image_paths)

            if result['success']:
                self.view.display_success(result['message'])
            else:
                self.view.display_error(result['message'])
        else:
            self.view.display_error("No image provided")

        self.view.pause()

    def view_student(self):
        """View student information"""
        print("\n" + "="*60)
        print("VIEW STUDENT INFORMATION")
        print("="*60)

        student_id = self.view.get_input("Enter Student ID")
        result = self.student_controller.get_student_info(student_id)

        if result['success']:
            self.view.display_student(result['student'])
        else:
            self.view.display_error(result['message'])

        self.view.pause()

    def list_students(self):
        """List all students"""
        print("\n" + "="*60)
        print("LIST ALL STUDENTS")
        print("="*60)

        result = self.student_controller.list_all_students()

        if result['success']:
            self.view.display_students_list(result['students'])
        else:
            self.view.display_error(result['message'])

        self.view.pause()

    def update_student(self):
        """Update student information"""
        print("\n" + "="*60)
        print("UPDATE STUDENT INFORMATION")
        print("="*60)

        student_id = self.view.get_input("Enter Student ID")

        # First, show current info
        result = self.student_controller.get_student_info(student_id)
        if not result['success']:
            self.view.display_error(result['message'])
            self.view.pause()
            return

        self.view.display_student(result['student'])

        print("\nEnter new values (press Enter to keep current):")
        full_name = self.view.get_input("Full Name")
        class_name = self.view.get_input("Class Name")
        email = self.view.get_input("Email")

        result = self.student_controller.update_student_info(
            student_id=student_id,
            full_name=full_name if full_name else None,
            class_name=class_name if class_name else None,
            email=email if email else None
        )

        if result['success']:
            self.view.display_success(result['message'])
        else:
            self.view.display_error(result['message'])

        self.view.pause()

    def delete_student(self):
        """Delete a student"""
        print("\n" + "="*60)
        print("DELETE STUDENT")
        print("="*60)

        student_id = self.view.get_input("Enter Student ID")

        confirm = self.view.get_input(f"Are you sure you want to delete student {student_id}? (yes/no)")

        if confirm.lower() == 'yes':
            result = self.student_controller.delete_student(student_id)

            if result['success']:
                self.view.display_success(result['message'])
            else:
                self.view.display_error(result['message'])
        else:
            self.view.display_info("Deletion cancelled")

        self.view.pause()

    def take_attendance_image(self):
        """Take attendance from image file"""
        print("\n" + "="*60)
        print("TAKE ATTENDANCE FROM IMAGE")
        print("="*60)
        print(f"Current model: {self.current_model}")

        image_path = self.view.get_input("Enter image file path")

        if not os.path.exists(image_path):
            self.view.display_error("Image file not found")
            self.view.pause()
            return

        self.view.display_info("Processing... Please wait.")

        result = self.attendance_controller.take_attendance_from_image(
            image_path=image_path,
            model_name=self.current_model
        )

        if result['success']:
            self.view.display_success(result['message'])
            print(f"\nStudent: {result['student_name']} ({result['student_id']})")
            print(f"Confidence: {result['confidence']:.2%}")
            print(f"Model: {result['model_used']}")
        else:
            self.view.display_error(result['message'])

        self.view.pause()

    def take_attendance_webcam(self):
        """Take attendance from webcam"""
        print("\n" + "="*60)
        print("TAKE ATTENDANCE FROM WEBCAM")
        print("="*60)
        print(f"Current model: {self.current_model}")

        temp_path = os.path.join(config.ATTENDANCE_LOG_PATH, f"temp_capture_{date.today()}.jpg")

        image_path = CameraUtility.capture_from_webcam(temp_path)

        if image_path:
            self.view.display_info("Processing... Please wait.")

            result = self.attendance_controller.take_attendance_from_image(
                image_path=image_path,
                model_name=self.current_model
            )

            if result['success']:
                self.view.display_success(result['message'])
                print(f"\nStudent: {result['student_name']} ({result['student_id']})")
                print(f"Confidence: {result['confidence']:.2%}")
                print(f"Model: {result['model_used']}")

                # Clean up temp file on success
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            else:
                self.view.display_error(result['message'])
                # Keep temp file for debugging when failed
                print(f"\n💡 Tip: Temp image saved at {temp_path} for debugging")
        else:
            self.view.display_error("No image captured")

        self.view.pause()

    def view_today_attendance(self):
        """View today's attendance"""
        print("\n" + "="*60)
        print("TODAY'S ATTENDANCE")
        print("="*60)

        result = self.attendance_controller.get_today_attendance()

        if result['success']:
            self.view.display_attendance_list(result['records'], result['date'])
        else:
            self.view.display_error(result['message'])

        self.view.pause()

    def view_attendance_by_date(self):
        """View attendance by date"""
        print("\n" + "="*60)
        print("VIEW ATTENDANCE BY DATE")
        print("="*60)

        session_date = self.view.get_input("Enter date (YYYY-MM-DD) or press Enter for today")

        if not session_date:
            session_date = None

        result = self.attendance_controller.get_attendance_by_date(session_date)

        if result['success']:
            self.view.display_attendance_list(result['records'], result['date'])
        else:
            self.view.display_error(result['message'])

        self.view.pause()

    def view_student_history(self):
        """View student attendance history"""
        print("\n" + "="*60)
        print("STUDENT ATTENDANCE HISTORY")
        print("="*60)

        student_id = self.view.get_input("Enter Student ID")

        result = self.attendance_controller.get_student_attendance_history(student_id)

        if result['success']:
            self.view.display_attendance_list(result['records'])
        else:
            self.view.display_error(result['message'])

        self.view.pause()

    def generate_report(self):
        """Generate attendance report"""
        print("\n" + "="*60)
        print("GENERATE ATTENDANCE REPORT")
        print("="*60)

        session_date = self.view.get_input("Enter date (YYYY-MM-DD) or press Enter for today")

        if not session_date:
            session_date = None

        result = self.attendance_controller.generate_report(session_date)

        if result['success']:
            self.view.display_attendance_report(result['report'])
            print("\nDetailed Records:")
            self.view.display_attendance_list(result['report']['records'], result['report']['date'])
        else:
            self.view.display_error(result['message'])

        self.view.pause()

    def change_model(self):
        """Change face recognition model"""
        print("\n" + "="*60)
        print("CHANGE RECOGNITION MODEL")
        print("="*60)

        result = self.attendance_controller.get_available_models()

        if result['success']:
            self.view.display_models_list(result['models'], self.current_model)

            model_choice = self.view.get_input("Enter model number or name")

            # Check if it's a number
            try:
                model_idx = int(model_choice) - 1
                if 0 <= model_idx < len(result['models']):
                    model_name = result['models'][model_idx]
                else:
                    self.view.display_error("Invalid model number")
                    self.view.pause()
                    return
            except ValueError:
                model_name = model_choice

            change_result = self.attendance_controller.change_recognition_model(model_name)

            if change_result['success']:
                self.current_model = model_name
                self.view.display_success(change_result['message'])
            else:
                self.view.display_error(change_result['message'])
        else:
            self.view.display_error(result['message'])

        self.view.pause()

    def view_models(self):
        """View available models"""
        print("\n" + "="*60)
        print("AVAILABLE MODELS")
        print("="*60)

        result = self.attendance_controller.get_available_models()

        if result['success']:
            self.view.display_models_list(result['models'], self.current_model)
        else:
            self.view.display_error(result['message'])

        self.view.pause()

    def test_recognition(self):
        """Test face recognition without marking attendance"""
        print("\n" + "="*60)
        print("TEST FACE RECOGNITION")
        print("="*60)
        print(f"Current model: {self.current_model}")

        img_choice = self.view.get_input("1. From file  2. From webcam (1/2)")

        image_path = None
        if img_choice == '1':
            image_path = self.view.get_input("Enter image file path")
        elif img_choice == '2':
            temp_path = os.path.join(config.ATTENDANCE_LOG_PATH, "test_capture.jpg")
            image_path = CameraUtility.capture_from_webcam(temp_path)

        if image_path and os.path.exists(image_path):
            self.view.display_info("Processing... Please wait.")

            result = self.face_controller.recognize_face(image_path, self.current_model)

            if result['success']:
                self.view.display_recognition_result(result)
            else:
                self.view.display_error(result['message'])
        else:
            self.view.display_error("No image provided or file not found")

        self.view.pause()

    def exit_application(self):
        """Exit the application"""
        self.running = False


def main():
    """Main entry point"""
    try:
        app = AttendanceApplication()
        app.run()
    except Exception as e:
        print(f"\nFatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

