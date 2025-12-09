# -*- coding: utf-8 -*-
"""
Khởi động ứng dụng GUI cho hệ thống điểm danh nhận diện khuôn mặt
"""
# Import các thư viện hệ thống cần thiết
import os  # Thư viện để xử lý đường dẫn file và thư mục
import sys  # Thư viện để truy cập các tham số và chức năng của hệ thống
import tkinter as tk  # Thư viện GUI Tkinter
from tkinter import filedialog, messagebox  # Các hộp thoại chọn file và thông báo
from datetime import date  # Thư viện để làm việc với ngày tháng

# Sử dụng UTF-8 trên Windows console
if sys.platform == 'win32':
    try:
        # Cấu hình lại encoding cho stdout và stderr thành UTF-8
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        # Bỏ qua nếu không cấu hình được
        pass

# import các module cần thiết từ src
from src.controllers.controllers import (
    StudentController,  # Controller quản lý sinh viên
    AttendanceController,  # Controller quản lý điểm danh
    FaceRecognitionController,  # Controller nhận diện khuôn mặt
    DataAugmentationController  # Controller tăng cường dữ liệu
)

# import các view và tiện ích
from src.views.tkinter_views import TkinterView  # View GUI Tkinter
from src.utils.utils import CameraUtility, ImageValidator  # Các tiện ích camera và xác thực ảnh
from src.config.config import config  # Cấu hình hệ thống

# Lớp chính của ứng dụng GUI
class AttendanceApplicationGUI:
    """Khởi động ứng dụng GUI cho hệ thống điểm danh nhận diện khuôn mặt"""

    # Khởi tạo ứng dụng
    def __init__(self, root: tk.Tk):
        """
        Khởi tạo ứng dụng GUI

        Args:
            root (tk.Tk): Cửa sổ gốc của Tkinter
        """
        self.root = root  # Tham chiếu đến cửa sổ gốc của Tkinter
        self.student_controller = StudentController()  # Khởi tạo controller quản lý sinh viên
        self.attendance_controller = AttendanceController()  # Khởi tạo controller điểm danh
        self.face_controller = FaceRecognitionController()  # Khởi tạo controller nhận diện khuôn mặt
        self.augmentation_controller = DataAugmentationController()  # Khởi tạo controller tăng cường dữ liệu
        self.view = TkinterView(root)  # Khởi tạo view Tkinter để tương tác với người dùng
        self.running = True  # Biến trạng thái chạy của ứng dụng
        self.current_model = config.DEFAULT_MODEL  # Mô hình nhận diện khuôn mặt hiện tại (mặc định từ config)

        # Hiển thị thông tin khởi tạo
        self.view.display_info(f"System initialized with model: {self.current_model}")

        # Khởi động menu chính
        self.show_menu()

    def show_menu(self):
        """Hiển thị menu chính"""
        # Gọi view để hiển thị menu và truyền hàm xử lý lựa chọn
        self.view.display_menu(self.handle_choice)

    # Xử lý lựa chọn từ menu
    def handle_choice(self, choice: str):
        """
        Xử lý lựa chọn từ menu

        Args:
            choice (str): Lựa chọn của người dùng (số hoặc chuỗi)
        """
        # Dictionary ánh xạ lựa chọn từ menu đến các phương thức tương ứng
        handlers = {
            '1': self.register_student,  # Đăng ký sinh viên mới
            '2': self.add_face_image,  # Thêm ảnh khuôn mặt
            '3': self.view_student,  # Xem thông tin sinh viên
            '4': self.list_students,  # Liệt kê tất cả sinh viên
            '5': self.update_student,  # Cập nhật thông tin sinh viên
            '6': self.delete_student,  # Xóa sinh viên
            '7': self.take_attendance_image,  # Điểm danh từ ảnh
            '8': self.take_attendance_webcam,  # Điểm danh từ webcam
            '9': self.view_today_attendance,  # Xem điểm danh hôm nay
            '10': self.view_attendance_by_date,  # Xem điểm danh theo ngày
            '11': self.view_student_history,  # Xem lịch sử điểm danh sinh viên
            '12': self.generate_report,  # Tạo báo cáo điểm danh
            '13': self.change_model,  # Thay đổi mô hình nhận diện
            '14': self.view_models,  # Xem danh sách mô hình
            '15': self.test_recognition,  # Kiểm tra nhận diện (không lưu)
            '16': self.augment_student_data,  # Tăng cường dữ liệu một sinh viên
            '17': self.augment_all_students_data,  # Tăng cường dữ liệu tất cả sinh viên
            '18': self.clean_augmented_data,  # Xóa ảnh đã tăng cường
            '0': self.exit_application  # Thoát ứng dụng
        }

        # Lấy hàm xử lý tương ứng với lựa chọn
        handler = handlers.get(choice)
        if handler:
            try:
                # Thử gọi hàm xử lý
                handler()
            except Exception as e:
                # Bắt và hiển thị lỗi nếu có
                self.view.display_error(f"Error: {str(e)}")
                import traceback
                # In thông tin chi tiết về lỗi
                traceback.print_exc()
        else:
            # Hiển thị thông báo lỗi nếu lựa chọn không hợp lệ
            self.view.display_error("Invalid choice. Please try again.")

    # Định nghĩa các phương thức chức năng
    def register_student(self):
        """
        Đăng ký sinh viên mới

        Cho phép người dùng nhập thông tin sinh viên và có thể thêm ảnh khuôn mặt
        Ảnh có thể chụp từ webcam hoặc chọn từ file
        """
        # Lấy ID sinh viên từ người dùng
        student_id = self.view.get_input("Enter Student ID")
        if not student_id:
            # Kiểm tra ID không được để trống
            self.view.display_error("Student ID cannot be empty")
            return

        # Lấy họ tên sinh viên
        full_name = self.view.get_input("Enter Full Name")
        if not full_name:
            # Kiểm tra họ tên không được để trống
            self.view.display_error("Full name cannot be empty")
            return

        # Lấy tên lớp
        class_name = self.view.get_input("Enter Class Name")
        # Lấy email (không bắt buộc)
        email = self.view.get_input("Enter Email (optional)")

        # Hỏi người dùng có muốn thêm ảnh khuôn mặt ngay không
        add_images = messagebox.askyesno("Add Images", "Add face images now?")
        # Biến lưu trữ đường dẫn ảnh
        image_paths = None

        # Nếu người dùng chọn thêm ảnh
        if add_images:
            # Hiển thị hộp thoại hỏi phương thức lấy ảnh
            choice = messagebox.askquestion(
                "Image Source",
                "Capture from webcam?\n\nYes = Webcam (multiple samples)\nNo = Select file",
                icon='question'
            )

            # Lấy ảnh từ webcam
            if choice == 'yes':
                # Thông báo số lượng ảnh mẫu sẽ chụp để cải thiện độ chính xác nhận diện
                self.view.display_info(f"Will capture {config.NUM_FACE_SAMPLES} face samples for better recognition")

                # Tạo đường dẫn thư mục lưu ảnh của sinh viên
                student_dir = os.path.join(config.STUDENT_DATABASE_PATH, student_id)
                # Chụp nhiều ảnh mẫu từ webcam
                image_paths = CameraUtility.capture_multiple_from_webcam(
                    save_dir=student_dir,  # Thư mục lưu ảnh
                    student_id=student_id,  # ID sinh viên
                    num_samples=config.NUM_FACE_SAMPLES,  # Số lượng ảnh mẫu lấy từ config
                    delay=config.SAMPLE_CAPTURE_DELAY  # Độ trễ giữa các lần chụp lấy từ config
                )

                # Nếu không có ảnh nào được chụp, hiển thị cảnh báo
                if not image_paths:
                    self.view.display_warning("No images captured")
            else:
                # Lấy ảnh từ file trên máy tính
                image_path = filedialog.askopenfilename(
                    title="Select face image",
                    filetypes=[("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")]
                )

                # Nếu có đường dẫn ảnh được chọn
                if image_path:
                    # Kiểm tra tính hợp lệ của ảnh (có chứa khuôn mặt không)
                    is_valid, message = ImageValidator.validate_face_image(image_path)
                    if is_valid:
                        # Nếu hợp lệ, thêm vào danh sách
                        image_paths = [image_path]
                    else:
                        # Nếu không hợp lệ, hiển thị thông báo lỗi
                        self.view.display_error(message)

        # Gọi controller để đăng ký sinh viên mới
        result = self.student_controller.register_new_student(
            student_id=student_id,  # ID sinh viên
            full_name=full_name,  # Họ tên
            class_name=class_name,  # Lớp
            email=email if email else None,  # Email (nếu có)
            image_paths=image_paths  # Danh sách đường dẫn ảnh (nếu có)
        )

        # Hiển thị kết quả
        if result['success']:
            # Nếu thành công, hiển thị thông báo và thông tin sinh viên
            self.view.display_success(result['message'])
            self.view.display_student(result['student'])
        else:
            # Nếu thất bại, hiển thị thông báo lỗi
            self.view.display_error(result['message'])

    def add_face_image(self):
        """Thêm ảnh khuôn mặt cho sinh viên đã tồn tại"""
        # Lấy ID sinh viên từ người dùng
        student_id = self.view.get_input("Enter Student ID")
        # Nếu không nhập ID, thoát khỏi hàm
        if not student_id:
            return

        # Hỏi người dùng chọn phương thức lấy ảnh
        choice = messagebox.askquestion(
            "Image Source",
            "Capture from webcam?\n\nYes = Webcam (multiple samples)\nNo = Select file",
            icon='question'
        )

        # Khởi tạo biến lưu đường dẫn ảnh
        image_paths = None
        # Nếu người dùng chọn chụp từ webcam
        if choice == 'yes':
            # Thông báo số lượng ảnh mẫu sẽ chụp
            self.view.display_info(f"Will capture {config.NUM_FACE_SAMPLES} face samples")

            # Tạo đường dẫn thư mục của sinh viên
            student_dir = os.path.join(config.STUDENT_DATABASE_PATH, student_id)
            # Chụp nhiều ảnh từ webcam
            image_paths = CameraUtility.capture_multiple_from_webcam(
                save_dir=student_dir,  # Thư mục lưu ảnh
                student_id=student_id,  # ID sinh viên
                num_samples=config.NUM_FACE_SAMPLES,  # Số lượng ảnh mẫu
                delay=config.SAMPLE_CAPTURE_DELAY  # Độ trễ giữa các lần chụp
            )
        else:
            # Nếu chọn file từ máy tính
            image_path = filedialog.askopenfilename(
                title="Select face image",
                filetypes=[("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")]
            )

            # Nếu có file được chọn
            if image_path:
                # Kiểm tra tính hợp lệ của ảnh
                is_valid, message = ImageValidator.validate_face_image(image_path)
                if is_valid:
                    # Thêm ảnh vào danh sách
                    image_paths = [image_path]
                else:
                    # Hiển thị lỗi nếu ảnh không hợp lệ
                    self.view.display_error(message)
                    return

        # Nếu có ảnh được cung cấp
        if image_paths:
            # Gọi controller để thêm ảnh vào cơ sở dữ liệu
            result = self.student_controller.add_face_image(student_id, image_paths=image_paths)

            # Hiển thị kết quả
            if result['success']:
                self.view.display_success(result['message'])
            else:
                self.view.display_error(result['message'])
        else:
            # Thông báo lỗi nếu không có ảnh
            self.view.display_error("No image provided")

    def view_student(self):
        """Xem thông tin sinh viên"""
        # Lấy ID sinh viên từ người dùng
        student_id = self.view.get_input("Enter Student ID")
        # Nếu không nhập ID, thoát khỏi hàm
        if not student_id:
            return

        # Gọi controller để lấy thông tin sinh viên
        result = self.student_controller.get_student_info(student_id)

        # Hiển thị kết quả
        if result['success']:
            # Hiển thị thông tin sinh viên
            self.view.display_student(result['student'])
        else:
            # Hiển thị lỗi nếu không tìm thấy
            self.view.display_error(result['message'])

    def list_students(self):
        """Liệt kê tất cả sinh viên"""
        # Gọi controller để lấy danh sách sinh viên
        result = self.student_controller.list_all_students()

        # Hiển thị kết quả
        if result['success']:
            # Hiển thị danh sách sinh viên
            self.view.display_students_list(result['students'])
        else:
            # Hiển thị lỗi nếu có vấn đề
            self.view.display_error(result['message'])

    def update_student(self):
        """Cập nhật thông tin sinh viên"""
        # Lấy ID sinh viên từ người dùng
        student_id = self.view.get_input("Enter Student ID")
        # Nếu không nhập ID, thoát khỏi hàm
        if not student_id:
            return

        # Đầu tiên, hiển thị thông tin hiện tại của sinh viên
        result = self.student_controller.get_student_info(student_id)
        # Nếu không tìm thấy sinh viên, hiển thị lỗi và thoát
        if not result['success']:
            self.view.display_error(result['message'])
            return

        # Hiển thị thông tin sinh viên
        self.view.display_student(result['student'])

        # Thông báo hướng dẫn cho người dùng
        messagebox.showinfo("Update", "Enter new values (leave empty to keep current)")

        # Lấy các giá trị mới từ người dùng
        full_name = self.view.get_input("Full Name (leave empty to keep current)")
        class_name = self.view.get_input("Class Name (leave empty to keep current)")
        email = self.view.get_input("Email (leave empty to keep current)")

        # Gọi controller để cập nhật thông tin
        result = self.student_controller.update_student_info(
            student_id=student_id,
            full_name=full_name if full_name else None,  # Chỉ cập nhật nếu có giá trị mới
            class_name=class_name if class_name else None,  # Chỉ cập nhật nếu có giá trị mới
            email=email if email else None  # Chỉ cập nhật nếu có giá trị mới
        )

        # Hiển thị kết quả
        if result['success']:
            self.view.display_success(result['message'])
        else:
            self.view.display_error(result['message'])

    def delete_student(self):
        """Xóa sinh viên"""
        # Lấy ID sinh viên từ người dùng
        student_id = self.view.get_input("Enter Student ID")
        # Nếu không nhập ID, thoát khỏi hàm
        if not student_id:
            return

        # Yêu cầu xác nhận xóa
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete student {student_id}?\n\nThis action cannot be undone."
        )

        # Nếu người dùng xác nhận
        if confirm:
            # Gọi controller để xóa sinh viên
            result = self.student_controller.delete_student(student_id)

            # Hiển thị kết quả
            if result['success']:
                self.view.display_success(result['message'])
            else:
                self.view.display_error(result['message'])

    def take_attendance_image(self):
        """Điểm danh từ file ảnh"""
        # Mở hộp thoại chọn file ảnh
        image_path = filedialog.askopenfilename(
            title="Select image for attendance",
            filetypes=[("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")]
        )

        # Nếu không chọn ảnh, thoát khỏi hàm
        if not image_path:
            return

        # Hiển thị thông báo đang xử lý
        self.view.show_processing("Processing... Please wait.")

        # Gọi controller để thực hiện điểm danh
        result = self.attendance_controller.take_attendance_from_image(
            image_path=image_path,  # Đường dẫn file ảnh
            model_name=self.current_model  # Mô hình nhận diện hiện tại
        )

        # Hiển thị kết quả
        if result['success']:
            # Tạo thông báo chi tiết về kết quả điểm danh
            message = f"{result['message']}\n\n"
            message += f"Student: {result['student_name']} ({result['student_id']})\n"
            message += f"Confidence: {result['confidence']:.2%}\n"  # Độ tin cậy dạng %
            message += f"Model: {result['model_used']}"  # Mô hình đã sử dụng
            self.view.display_success(message)
        else:
            # Hiển thị lỗi nếu không nhận diện được
            self.view.display_error(result['message'])

    def take_attendance_webcam(self):
        """Điểm danh từ webcam"""
        # Tạo đường dẫn file tạm để lưu ảnh chụp từ webcam
        temp_path = os.path.join(config.ATTENDANCE_LOG_PATH, f"temp_capture_{date.today()}.jpg")

        # Chụp ảnh từ webcam
        image_path = CameraUtility.capture_from_webcam(temp_path)

        # Nếu chụp ảnh thành công
        if image_path:
            # Hiển thị thông báo đang xử lý
            self.view.show_processing("Processing... Please wait.")

            # Gọi controller để thực hiện điểm danh
            result = self.attendance_controller.take_attendance_from_image(
                image_path=image_path,  # Đường dẫn ảnh vừa chụp
                model_name=self.current_model  # Mô hình nhận diện hiện tại
            )

            # Hiển thị kết quả
            if result['success']:
                # Tạo thông báo chi tiết về kết quả điểm danh
                message = f"{result['message']}\n\n"
                message += f"Student: {result['student_name']} ({result['student_id']})\n"
                message += f"Confidence: {result['confidence']:.2%}\n"  # Độ tin cậy dạng %
                message += f"Model: {result['model_used']}"  # Mô hình đã sử dụng
                self.view.display_success(message)

                # Xóa file tạm sau khi điểm danh thành công
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            else:
                # Hiển thị lỗi nếu không nhận diện được
                self.view.display_error(result['message'])
        else:
            # Thông báo lỗi nếu không chụp được ảnh
            self.view.display_error("No image captured")

    def view_today_attendance(self):
        """Xem danh sách điểm danh hôm nay"""
        # Gọi controller để lấy danh sách điểm danh hôm nay
        result = self.attendance_controller.get_today_attendance()

        # Hiển thị kết quả
        if result['success']:
            # Hiển thị danh sách điểm danh với ngày tháng
            self.view.display_attendance_list(result['records'], result['date'])
        else:
            # Hiển thị lỗi nếu có vấn đề
            self.view.display_error(result['message'])

    def view_attendance_by_date(self):
        """Xem danh sách điểm danh theo ngày"""
        # Lấy ngày từ người dùng (hoặc để trống để xem hôm nay)
        session_date = self.view.get_input("Enter date (YYYY-MM-DD) or leave empty for today")

        # Nếu không nhập ngày, đặt là None (sẽ dùng ngày hôm nay)
        if not session_date:
            session_date = None

        # Gọi controller để lấy danh sách điểm danh theo ngày
        result = self.attendance_controller.get_attendance_by_date(session_date)

        # Hiển thị kết quả
        if result['success']:
            # Hiển thị danh sách điểm danh với ngày tháng
            self.view.display_attendance_list(result['records'], result['date'])
        else:
            # Hiển thị lỗi nếu có vấn đề
            self.view.display_error(result['message'])

    def view_student_history(self):
        """Xem lịch sử điểm danh của sinh viên"""
        # Lấy ID sinh viên từ người dùng
        student_id = self.view.get_input("Enter Student ID")
        # Nếu không nhập ID, thoát khỏi hàm
        if not student_id:
            return

        # Gọi controller để lấy lịch sử điểm danh của sinh viên
        result = self.attendance_controller.get_student_attendance_history(student_id)

        # Hiển thị kết quả
        if result['success']:
            # Hiển thị danh sách lịch sử điểm danh
            self.view.display_attendance_list(result['records'])
        else:
            # Hiển thị lỗi nếu có vấn đề
            self.view.display_error(result['message'])

    def generate_report(self):
        """Tạo báo cáo điểm danh"""
        # Lấy ngày từ người dùng (hoặc để trống để tạo báo cáo hôm nay)
        session_date = self.view.get_input("Enter date (YYYY-MM-DD) or leave empty for today")

        # Nếu không nhập ngày, đặt là None (sẽ dùng ngày hôm nay)
        if not session_date:
            session_date = None

        # Gọi controller để tạo báo cáo
        result = self.attendance_controller.generate_report(session_date)

        # Hiển thị kết quả
        if result['success']:
            # Hiển thị báo cáo thống kê
            self.view.display_attendance_report(result['report'])
            # Cũng hiển thị danh sách chi tiết
            self.view.display_attendance_list(result['report']['records'], result['report']['date'])
        else:
            # Hiển thị lỗi nếu có vấn đề
            self.view.display_error(result['message'])

    def change_model(self):
        """Thay đổi mô hình nhận diện khuôn mặt"""
        # Lấy danh sách các mô hình có sẵn
        result = self.attendance_controller.get_available_models()

        # Nếu lấy danh sách thành công
        if result['success']:
            # Hiển thị danh sách các mô hình và mô hình hiện tại
            self.view.display_models_list(result['models'], self.current_model)

            # Hỏi người dùng chọn mô hình (có thể nhập số thứ tự hoặc tên mô hình)
            model_choice = self.view.get_input("Enter model number or name")
            if not model_choice:
                return

            # Kiểm tra xem người dùng nhập số hay tên
            try:
                # Thử chuyển đổi sang số (chỉ số trong danh sách)
                model_idx = int(model_choice) - 1
                # Kiểm tra xem chỉ số có hợp lệ không
                if 0 <= model_idx < len(result['models']):
                    # Lấy tên mô hình từ danh sách
                    model_name = result['models'][model_idx]
                else:
                    # Chỉ số không hợp lệ
                    self.view.display_error("Invalid model number")
                    return
            except ValueError:
                # Nếu không phải số, coi như là tên mô hình
                model_name = model_choice

            # Gọi controller để thay đổi mô hình
            change_result = self.attendance_controller.change_recognition_model(model_name)

            # Hiển thị kết quả
            if change_result['success']:
                # Cập nhật mô hình hiện tại
                self.current_model = model_name
                self.view.display_success(change_result['message'])
            else:
                # Hiển thị lỗi nếu có vấn đề
                self.view.display_error(change_result['message'])
        else:
            # Hiển thị lỗi nếu không lấy được danh sách
            self.view.display_error(result['message'])

    def view_models(self):
        """Xem danh sách các mô hình có sẵn"""
        # Lấy danh sách các mô hình có sẵn
        result = self.attendance_controller.get_available_models()

        # Hiển thị kết quả
        if result['success']:
            # Hiển thị danh sách các mô hình và mô hình hiện tại
            self.view.display_models_list(result['models'], self.current_model)
        else:
            # Hiển thị lỗi nếu có vấn đề
            self.view.display_error(result['message'])

    def test_recognition(self):
        """Kiểm tra nhận diện khuôn mặt mà không đánh dấu điểm danh"""
        # Hỏi người dùng chọn nguồn ảnh
        choice = messagebox.askquestion(
            "Image Source",
            "Capture from webcam?\n\nYes = Webcam\nNo = Select file",
            icon='question'
        )

        # Khởi tạo biến lưu đường dẫn ảnh
        image_path = None
        # Nếu chọn chụp từ webcam
        if choice == 'yes':
            # Tạo đường dẫn file tạm để lưu ảnh test
            temp_path = os.path.join(config.ATTENDANCE_LOG_PATH, "test_capture.jpg")
            # Chụp ảnh từ webcam
            image_path = CameraUtility.capture_from_webcam(temp_path)
        else:
            # Nếu chọn file từ máy tính
            image_path = filedialog.askopenfilename(
                title="Select image to test",
                filetypes=[("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")]
            )

        # Nếu có ảnh và file tồn tại
        if image_path and os.path.exists(image_path):
            # Hiển thị thông báo đang xử lý
            self.view.show_processing("Processing... Please wait.")

            # Gọi controller để nhận diện khuôn mặt (không ghi điểm danh)
            result = self.face_controller.recognize_face(image_path, self.current_model)

            # Hiển thị kết quả
            if result['success']:
                # Hiển thị kết quả nhận diện
                self.view.display_recognition_result(result)
            else:
                # Hiển thị lỗi nếu không nhận diện được
                self.view.display_error(result['message'])
        else:
            # Thông báo lỗi nếu không có ảnh hoặc file không tồn tại
            self.view.display_error("No image provided or file not found")

    def augment_student_data(self):
        """Tăng cường dữ liệu cho một sinh viên"""
        # Lấy ID sinh viên từ người dùng
        student_id = self.view.get_input("Enter Student ID")
        # Nếu không nhập ID, thoát khỏi hàm
        if not student_id:
            return

        # Hỏi số lượng ảnh tăng cường cho mỗi ảnh gốc
        num_str = self.view.get_input("Number of augmented images per original (default: 5)")
        try:
            # Chuyển đổi sang số nguyên, mặc định là 5
            num_augmented = int(num_str) if num_str else 5
            # Kiểm tra giá trị hợp lệ (từ 1 đến 20)
            if num_augmented < 1 or num_augmented > 20:
                self.view.display_error("Number must be between 1 and 20")
                return
        except ValueError:
            # Nếu nhập không phải số, hiển thị lỗi
            self.view.display_error("Invalid number")
            return

        # Yêu cầu xác nhận từ người dùng
        confirm = messagebox.askyesno(
            "Confirm Augmentation",
            f"This will create {num_augmented} augmented images per original image for student {student_id}.\n\n"
            "This improves recognition accuracy!\n\nContinue?"
        )

        # Nếu không xác nhận, thoát
        if not confirm:
            return

        # Hiển thị thông báo đang xử lý
        self.view.show_processing("Augmenting data... Please wait.")

        # Gọi controller để tăng cường dữ liệu
        result = self.augmentation_controller.augment_student(student_id, num_augmented)

        # Hiển thị kết quả
        if result['success']:
            # Tạo thông báo chi tiết về kết quả
            message = f"{result['message']}\n\n"
            message += f"Original images: {result['original_images']}\n"  # Số ảnh gốc
            message += f"Augmented images: {result['augmented_images']}\n"  # Số ảnh tăng cường
            message += f"Total images now: {result['total_images']}"  # Tổng số ảnh hiện tại
            self.view.display_success(message)
        else:
            # Hiển thị lỗi nếu có vấn đề
            self.view.display_error(result['message'])

    def augment_all_students_data(self):
        """Tăng cường dữ liệu cho tất cả sinh viên"""
        # Hỏi số lượng ảnh tăng cường cho mỗi ảnh gốc
        num_str = self.view.get_input("Number of augmented images per original (default: 5)")
        try:
            # Chuyển đổi sang số nguyên, mặc định là 5
            num_augmented = int(num_str) if num_str else 5
            # Kiểm tra giá trị hợp lệ (từ 1 đến 20)
            if num_augmented < 1 or num_augmented > 20:
                self.view.display_error("Number must be between 1 and 20")
                return
        except ValueError:
            # Nếu nhập không phải số, hiển thị lỗi
            self.view.display_error("Invalid number")
            return

        # Yêu cầu xác nhận từ người dùng (đây là thao tác lớn)
        confirm = messagebox.askyesno(
            "Confirm Mass Augmentation",
            f"This will augment data for ALL students!\n\n"
            f"Creating {num_augmented} images per original.\n"
            "This may take several minutes.\n\n"
            "Continue?"
        )

        # Nếu không xác nhận, thoát
        if not confirm:
            return

        # Hiển thị thông báo đang xử lý (quá trình này có thể mất nhiều thời gian)
        self.view.show_processing("Augmenting all students... This may take a while.")

        # Gọi controller để tăng cường dữ liệu cho tất cả sinh viên
        result = self.augmentation_controller.augment_all_students(num_augmented)

        # Hiển thị kết quả
        if result['success']:
            # Lấy thống kê từ kết quả
            stats = result['stats']
            # Tạo thông báo chi tiết
            message = f"{result['message']}\n\n"
            message += f"Students processed: {stats['students_processed']}\n"  # Số sinh viên đã xử lý
            message += f"Original images: {stats['original_images']}\n"  # Tổng số ảnh gốc
            message += f"Augmented images: {stats['augmented_images']}\n"  # Tổng số ảnh tăng cường
            message += f"Total images now: {stats['original_images'] + stats['augmented_images']}"  # Tổng số ảnh hiện tại

            # Nếu có lỗi trong quá trình xử lý, thêm thông tin
            if stats['errors']:
                message += f"\n\nErrors: {len(stats['errors'])}"

            self.view.display_success(message)
        else:
            # Hiển thị lỗi nếu có vấn đề
            self.view.display_error(result['message'])

    def clean_augmented_data(self):
        """Xóa các ảnh đã tăng cường"""
        # Hỏi phạm vi xóa
        choice = messagebox.askquestion(
            "Clean Scope",
            "Clean all students?\n\nYes = All students\nNo = Single student",
            icon='question'
        )

        # Khởi tạo biến student_id
        student_id = None
        # Nếu chọn xóa cho một sinh viên cụ thể
        if choice == 'no':
            # Lấy ID sinh viên
            student_id = self.view.get_input("Enter Student ID")
            if not student_id:
                return

        # Xác nhận xóa
        scope_text = "ALL STUDENTS" if not student_id else f"student {student_id}"
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"This will delete all augmented images for {scope_text}.\n\n"
            "Original images will NOT be affected.\n\n"  # Ảnh gốc sẽ không bị ảnh hưởng
            "Continue?"
        )

        # Nếu không xác nhận, thoát
        if not confirm:
            return

        # Gọi controller để xóa ảnh tăng cường
        result = self.augmentation_controller.clean_augmented_images(student_id)

        # Hiển thị kết quả
        if result['success']:
            # Hiển thị thông báo thành công và số lượng file đã xóa
            self.view.display_success(f"{result['message']}\n\nDeleted: {result['deleted_count']} files")
        else:
            # Hiển thị lỗi nếu có vấn đề
            self.view.display_error(result['message'])

    def exit_application(self):
        """Thoát khỏi ứng dụng"""
        # Xác nhận thoát
        confirm = messagebox.askyesno(
            "Exit",
            "Are you sure you want to exit?"
        )
        # Nếu xác nhận, thoát ứng dụng
        if confirm:
            self.root.quit()


def main():
    """Điểm khởi động chính của chương trình"""
    try:
        # Tạo cửa sổ Tkinter gốc
        root = tk.Tk()
        # Khởi tạo ứng dụng GUI
        app = AttendanceApplicationGUI(root)
        # Chạy vòng lặp sự kiện chính của Tkinter
        root.mainloop()
    except Exception as e:
        # Bắt và hiển thị lỗi nghiêm trọng
        messagebox.showerror("Fatal Error", f"Fatal error: {str(e)}")
        import traceback
        # In thông tin chi tiết về lỗi
        traceback.print_exc()
        # Thoát chương trình với mã lỗi
        sys.exit(1)


if __name__ == "__main__":
    # Chạy hàm main nếu file được thực thi trực tiếp
    main()

