"""
Lớp View GUI sử dụng Tkinter cho Hệ thống điểm danh nhận diện khuôn mặt
"""
# Import các thư viện cần thiết
import tkinter as tk  # Thư viện GUI Tkinter
from tkinter import ttk, messagebox, simpledialog, scrolledtext  # Các widget và hộp thoại
from typing import Dict, Any, List, Optional, Callable  # Type hints để định nghĩa kiểu dữ liệu
from datetime import datetime  # Thư viện xử lý ngày giờ
from src.models.models import Student, AttendanceRecord  # Import models sinh viên và điểm danh
import threading  # Thư viện xử lý đa luồng


class TkinterView:
    """Lớp View GUI sử dụng Tkinter"""

    def __init__(self, root: tk.Tk):
        """
        Khởi tạo giao diện Tkinter

        Args:
            root (tk.Tk): Cửa sổ gốc của Tkinter
        """
        self.root = root  # Lưu tham chiếu đến cửa sổ gốc
        self.root.title("Face Recognition Attendance System")  # Đặt tiêu đề cửa sổ
        self.root.geometry("900x700")  # Đặt kích thước cửa sổ

        # Cấu hình theme/style cho giao diện
        self.style = ttk.Style()  # Tạo đối tượng style
        self.style.theme_use('clam')  # Sử dụng theme 'clam'

        # Định nghĩa bảng màu cho giao diện
        self.bg_color = "#f0f0f0"  # Màu nền chính (xám nhạt)
        self.primary_color = "#2196F3"  # Màu chính (xanh dương)
        self.success_color = "#4CAF50"  # Màu thành công (xanh lá)
        self.error_color = "#f44336"  # Màu lỗi (đỏ)
        self.warning_color = "#FF9800"  # Màu cảnh báo (cam)

        self.root.configure(bg=self.bg_color)  # Áp dụng màu nền cho cửa sổ gốc

        # Các biến để xử lý input callback (lấy input từ người dùng)
        self._input_callback = None  # Hàm callback khi có input
        self._input_result = None  # Kết quả input từ người dùng

    def display_menu(self, callback: Callable[[str], None]):
        """
        Hiển thị menu chính dưới dạng các nút bấm

        Args:
            callback: Hàm callback được gọi khi người dùng chọn một menu
        """
        # Xóa tất cả các widget hiện tại trên cửa sổ
        for widget in self.root.winfo_children():
            widget.destroy()

        # Tạo khung tiêu đề ở đầu cửa sổ
        title_frame = tk.Frame(self.root, bg=self.primary_color, height=60)
        title_frame.pack(fill=tk.X)  # Lấp đầy theo chiều ngang
        title_frame.pack_propagate(False)  # Không cho frame tự động thay đổi kích thước

        # Nhãn tiêu đề
        title_label = tk.Label(
            title_frame,
            text="FACE RECOGNITION ATTENDANCE SYSTEM",
            font=("Arial", 16, "bold"),
            bg=self.primary_color,
            fg="white"
        )
        title_label.pack(pady=15)

        # Container chính với thanh cuộn
        main_container = tk.Frame(self.root, bg=self.bg_color)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Tạo canvas để có thể cuộn
        canvas = tk.Canvas(main_container, bg=self.bg_color, highlightthickness=0)
        # Thanh cuộn dọc
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        # Frame có thể cuộn chứa các nút menu
        scrollable_frame = tk.Frame(canvas, bg=self.bg_color)

        # Bind sự kiện để cập nhật vùng cuộn khi frame thay đổi
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # Tạo cửa sổ trong canvas để chứa frame
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Đặt canvas và scrollbar vào container
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Định nghĩa các phần menu với các nút tương ứng
        sections = [
            ("STUDENT MANAGEMENT", [  # Quản lý sinh viên
                ("1", "Register new student", self.primary_color),  # Đăng ký sinh viên mới
                ("2", "Add face image to student", self.primary_color),  # Thêm ảnh khuôn mặt
                ("3", "View student information", self.primary_color),  # Xem thông tin sinh viên
                ("4", "List all students", self.primary_color),  # Liệt kê tất cả sinh viên
                ("5", "Update student information", self.primary_color),  # Cập nhật thông tin
                ("6", "Delete student", self.error_color),  # Xóa sinh viên
            ]),
            ("ATTENDANCE", [  # Điểm danh
                ("7", "Take attendance from image", self.success_color),  # Điểm danh từ ảnh
                ("8", "Take attendance from webcam", self.success_color),  # Điểm danh từ webcam
                ("9", "View today's attendance", self.primary_color),  # Xem điểm danh hôm nay
                ("10", "View attendance by date", self.primary_color),  # Xem điểm danh theo ngày
                ("11", "View student attendance history", self.primary_color),  # Xem lịch sử điểm danh
                ("12", "Generate attendance report", self.primary_color),  # Tạo báo cáo điểm danh
            ]),
            ("DATA AUGMENTATION - VGGFace2 Inspired", [  # Tăng cường dữ liệu
                ("16", "Augment student data (single)", "#9C27B0"),  # Tăng cường cho một sinh viên
                ("17", "Augment all students data", "#9C27B0"),  # Tăng cường cho tất cả
                ("18", "Clean augmented images", self.warning_color),  # Xóa ảnh đã tăng cường
            ]),
            ("SETTINGS", [  # Cài đặt
                ("13", "Change recognition model", self.warning_color),  # Thay đổi mô hình nhận diện
                ("14", "View available models", self.primary_color),  # Xem danh sách mô hình
            ]),
            ("OTHER", [  # Khác
                ("15", "Test face recognition", self.warning_color),  # Kiểm tra nhận diện
                ("0", "Exit", self.error_color),  # Thoát
            ])
        ]

        # Duyệt qua từng section và tạo giao diện
        for section_name, buttons in sections:
            # Tạo khung cho mỗi section với tiêu đề
            section_frame = tk.LabelFrame(
                scrollable_frame,
                text=section_name,
                font=("Arial", 11, "bold"),
                bg=self.bg_color,
                fg="#333333"
            )
            section_frame.pack(fill=tk.X, pady=10)

            # Tạo các nút trong section
            for choice, text, color in buttons:
                btn = tk.Button(
                    section_frame,
                    text=f"{choice}. {text}",  # Hiển thị số và tên chức năng
                    font=("Arial", 10),
                    bg=color,  # Màu nền của nút
                    fg="white",  # Màu chữ trắng
                    activebackground=color,  # Màu khi nút được nhấn
                    activeforeground="white",
                    cursor="hand2",  # Con trỏ chuột dạng bàn tay
                    relief=tk.FLAT,  # Kiểu nút phẳng
                    padx=20,
                    pady=10,
                    command=lambda c=choice: callback(c)  # Gọi callback khi click
                )
                btn.pack(fill=tk.X, padx=10, pady=5)

    def display_success(self, message: str):
        """
        Hiển thị thông báo thành công

        Args:
            message: Nội dung thông báo
        """
        messagebox.showinfo("Success", message)

    def display_error(self, message: str):
        """
        Hiển thị thông báo lỗi

        Args:
            message: Nội dung lỗi
        """
        messagebox.showerror("Error", message)

    def display_info(self, message: str):
        """
        Hiển thị thông báo thông tin

        Args:
            message: Nội dung thông tin
        """
        messagebox.showinfo("Information", message)

    def display_warning(self, message: str):
        """
        Hiển thị thông báo cảnh báo

        Args:
            message: Nội dung cảnh báo
        """
        messagebox.showwarning("Warning", message)

    def get_input(self, prompt: str) -> str:
        """
        Lấy input từ người dùng qua hộp thoại

        Args:
            prompt: Thông điệp nhắc nhở người dùng nhập

        Returns:
            str: Chuỗi người dùng nhập vào (hoặc rỗng nếu cancel)
        """
        result = simpledialog.askstring("Input", prompt, parent=self.root)
        return result if result else ""

    def get_choice(self) -> str:
        """
        Lấy lựa chọn menu (không sử dụng trong chế độ GUI)

        Returns:
            str: Chuỗi rỗng
        """
        return ""

    def pause(self):
        """Tạm dừng (không cần thiết trong chế độ GUI)"""
        pass

    def display_student(self, student: Student):
        """
        Hiển thị thông tin sinh viên trong cửa sổ mới

        Args:
            student: Đối tượng Student chứa thông tin sinh viên
        """
        # Tạo cửa sổ con mới (Toplevel)
        win = tk.Toplevel(self.root)
        win.title("Student Information")  # Tiêu đề cửa sổ
        win.geometry("500x400")  # Kích thước cửa sổ
        win.configure(bg=self.bg_color)  # Màu nền

        # Tiêu đề
        title = tk.Label(
            win,
            text="STUDENT INFORMATION",
            font=("Arial", 14, "bold"),
            bg=self.primary_color,
            fg="white",
            pady=10
        )
        title.pack(fill=tk.X)  # Lấp đầy theo chiều ngang

        # Khung nội dung chính
        content = tk.Frame(win, bg=self.bg_color)
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Danh sách các trường thông tin sinh viên
        details = [
            ("Student ID:", student.student_id),
            ("Full Name:", student.full_name),
            ("Class:", student.class_name),
            ("Email:", student.email or "N/A"),  # Hiển thị N/A nếu không có email
            ("Face Image:", "Registered" if student.face_encoding_path else "Not registered"),
            ("Created:", student.created_at.strftime('%Y-%m-%d %H:%M:%S'))  # Định dạng ngày giờ
        ]

        # Hiển thị từng trường thông tin dạng lưới (grid)
        for i, (label, value) in enumerate(details):
            # Cột 0: Nhãn (in đậm)
            lbl = tk.Label(content, text=label, font=("Arial", 10, "bold"), bg=self.bg_color, anchor="w")
            lbl.grid(row=i, column=0, sticky="w", pady=5, padx=5)

            # Cột 1: Giá trị
            val = tk.Label(content, text=value, font=("Arial", 10), bg=self.bg_color, anchor="w")
            val.grid(row=i, column=1, sticky="w", pady=5, padx=5)

        # Nút đóng cửa sổ
        close_btn = tk.Button(
            win,
            text="Close",
            command=win.destroy,  # Đóng cửa sổ khi click
            bg=self.primary_color,
            fg="white",
            font=("Arial", 10),
            cursor="hand2",
            padx=20,
            pady=5
        )
        close_btn.pack(pady=10)

    def display_students_list(self, students: List[Student]):
        """
        Hiển thị danh sách sinh viên trong cửa sổ mới với Treeview

        Args:
            students: Danh sách các đối tượng Student
        """
        # Tạo cửa sổ mới
        win = tk.Toplevel(self.root)
        win.title("Students List")
        win.geometry("900x500")
        win.configure(bg=self.bg_color)

        # Tiêu đề với tổng số sinh viên
        title = tk.Label(
            win,
            text=f"ALL STUDENTS (Total: {len(students)})",
            font=("Arial", 14, "bold"),
            bg=self.primary_color,
            fg="white",
            pady=10
        )
        title.pack(fill=tk.X)

        # Nếu không có sinh viên nào
        if not students:
            msg = tk.Label(win, text="No students found.", font=("Arial", 12), bg=self.bg_color)
            msg.pack(pady=50)
            return

        # Tạo khung chứa Treeview
        frame = tk.Frame(win, bg=self.bg_color)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Tạo Treeview để hiển thị dữ liệu dạng bảng
        tree = ttk.Treeview(
            frame,
            columns=("ID", "Name", "Class", "Email", "Face"),  # Các cột
            show="headings",  # Chỉ hiển thị tiêu đề cột
            height=15
        )

        # Cấu hình tiêu đề các cột
        tree.heading("ID", text="Student ID")
        tree.heading("Name", text="Full Name")
        tree.heading("Class", text="Class")
        tree.heading("Email", text="Email")
        tree.heading("Face", text="Face")

        # Cấu hình độ rộng các cột
        tree.column("ID", width=120)
        tree.column("Name", width=200)
        tree.column("Class", width=150)
        tree.column("Email", width=200)
        tree.column("Face", width=80)

        # Thanh cuộn dọc
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        # Thêm dữ liệu sinh viên vào bảng
        for student in students:
            face_status = "✓" if student.face_encoding_path else "✗"  # Ký hiệu có/không có ảnh
            email = student.email if student.email else "N/A"
            tree.insert("", "end", values=(
                student.student_id,
                student.full_name,
                student.class_name,
                email,
                face_status
            ))

        # Đặt tree và scrollbar
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Nút đóng
        close_btn = tk.Button(
            win,
            text="Close",
            command=win.destroy,
            bg=self.primary_color,
            fg="white",
            font=("Arial", 10),
            cursor="hand2",
            padx=20,
            pady=5
        )
        close_btn.pack(pady=10)

    def display_attendance_list(self, records: List[AttendanceRecord], date: str = None):
        """
        Hiển thị danh sách các bản ghi điểm danh

        Args:
            records: Danh sách các bản ghi điểm danh
            date: Ngày điểm danh (tùy chọn)
        """
        win = tk.Toplevel(self.root)
        title_text = f"Attendance Records - {date}" if date else "Attendance Records"
        win.title(title_text)
        win.geometry("900x500")
        win.configure(bg=self.bg_color)

        # Tiêu đề
        title = tk.Label(
            win,
            text=f"{title_text.upper()} (Total: {len(records)})",
            font=("Arial", 14, "bold"),
            bg=self.primary_color,
            fg="white",
            pady=10
        )
        title.pack(fill=tk.X)

        if not records:
            msg = tk.Label(win, text="No attendance records found.", font=("Arial", 12), bg=self.bg_color)
            msg.pack(pady=50)
            return

        # Treeview
        frame = tk.Frame(win, bg=self.bg_color)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tree = ttk.Treeview(
            frame,
            columns=("ID", "Time", "Status", "Confidence", "Model"),
            show="headings",
            height=15
        )

        # Cấu hình cột
        tree.heading("ID", text="Student ID")
        tree.heading("Time", text="Check-in Time")
        tree.heading("Status", text="Status")
        tree.heading("Confidence", text="Confidence")
        tree.heading("Model", text="Model")

        tree.column("ID", width=120)
        tree.column("Time", width=180)
        tree.column("Status", width=100)
        tree.column("Confidence", width=100)
        tree.column("Model", width=150)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        # Thêm dữ liệu
        for record in records:
            check_in = record.check_in_time.strftime('%Y-%m-%d %H:%M:%S')
            confidence = f"{record.confidence:.2%}" if record.confidence else "N/A"
            tree.insert("", "end", values=(
                record.student_id,
                check_in,
                record.status,
                confidence,
                record.model_used
            ))

        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Nút đóng
        close_btn = tk.Button(
            win,
            text="Close",
            command=win.destroy,
            bg=self.primary_color,
            fg="white",
            font=("Arial", 10),
            cursor="hand2",
            padx=20,
            pady=5
        )
        close_btn.pack(pady=10)

    def display_attendance_report(self, report: Dict[str, Any]):
        """
        Hiển thị báo cáo thống kê điểm danh

        Args:
            report: Dictionary chứa thông tin báo cáo
        """
        win = tk.Toplevel(self.root)
        win.title("Attendance Report")
        win.geometry("500x350")
        win.configure(bg=self.bg_color)

        # Tiêu đề
        title = tk.Label(
            win,
            text=f"ATTENDANCE REPORT - {report['date']}",
            font=("Arial", 14, "bold"),
            bg=self.primary_color,
            fg="white",
            pady=10
        )
        title.pack(fill=tk.X)

        # Khung nội dung
        content = tk.Frame(win, bg=self.bg_color)
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Chi tiết báo cáo
        total = report['total_records']
        present_pct = f"({report['present']/total*100:.1f}%)" if total > 0 else ""

        details = [
            ("Total Records:", str(total)),
            ("Present:", f"{report['present']} {present_pct}"),
            ("Late:", str(report['late'])),
            ("Absent:", str(report['absent']))
        ]

        for i, (label, value) in enumerate(details):
            lbl = tk.Label(content, text=label, font=("Arial", 12, "bold"), bg=self.bg_color, anchor="w")
            lbl.grid(row=i, column=0, sticky="w", pady=10, padx=10)

            val = tk.Label(content, text=value, font=("Arial", 12), bg=self.bg_color, anchor="w")
            val.grid(row=i, column=1, sticky="w", pady=10, padx=10)

        # Nút đóng
        close_btn = tk.Button(
            win,
            text="Close",
            command=win.destroy,
            bg=self.primary_color,
            fg="white",
            font=("Arial", 10),
            cursor="hand2",
            padx=20,
            pady=5
        )
        close_btn.pack(pady=10)

    def display_recognition_result(self, result: Dict[str, Any]):
        """
        Hiển thị kết quả nhận diện khuôn mặt

        Args:
            result: Dictionary chứa kết quả nhận diện
        """
        win = tk.Toplevel(self.root)
        win.title("Recognition Result")
        win.geometry("500x350")
        win.configure(bg=self.bg_color)

        if result.get('recognized', False):
            # Nhận diện thành công
            title_bg = self.success_color
            title_text = "✓ FACE RECOGNIZED"

            title = tk.Label(
                win,
                text=title_text,
                font=("Arial", 14, "bold"),
                bg=title_bg,
                fg="white",
                pady=10
            )
            title.pack(fill=tk.X)

            # Nội dung
            content = tk.Frame(win, bg=self.bg_color)
            content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

            rec_result = result['result']
            details = [
                ("Student ID:", rec_result.student_id),
                ("Name:", rec_result.student_name),
                ("Confidence:", f"{rec_result.confidence:.2%}"),
                ("Distance:", f"{rec_result.distance:.4f}"),
                ("Model Used:", rec_result.model_used)
            ]

            for i, (label, value) in enumerate(details):
                lbl = tk.Label(content, text=label, font=("Arial", 11, "bold"), bg=self.bg_color, anchor="w")
                lbl.grid(row=i, column=0, sticky="w", pady=8, padx=10)

                val = tk.Label(content, text=value, font=("Arial", 11), bg=self.bg_color, anchor="w")
                val.grid(row=i, column=1, sticky="w", pady=8, padx=10)
        else:
            # Không nhận diện được
            title_bg = self.error_color
            title_text = "✗ FACE NOT RECOGNIZED"

            title = tk.Label(
                win,
                text=title_text,
                font=("Arial", 14, "bold"),
                bg=title_bg,
                fg="white",
                pady=10
            )
            title.pack(fill=tk.X)

            content = tk.Frame(win, bg=self.bg_color)
            content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

            msg = tk.Label(
                content,
                text="No matching face found in database.",
                font=("Arial", 11),
                bg=self.bg_color
            )
            msg.pack(pady=20)

            if 'result' in result:
                rec_result = result['result']
                model_lbl = tk.Label(content, text=f"Model Used: {rec_result.model_used}", font=("Arial", 10), bg=self.bg_color)
                model_lbl.pack()

        # Nút đóng
        close_btn = tk.Button(
            win,
            text="Close",
            command=win.destroy,
            bg=self.primary_color,
            fg="white",
            font=("Arial", 10),
            cursor="hand2",
            padx=20,
            pady=5
        )
        close_btn.pack(pady=10)

    def display_models_list(self, models: List[str], current: str = None):
        """
        Hiển thị danh sách các mô hình nhận diện có sẵn

        Args:
            models: Danh sách tên các mô hình
            current: Mô hình đang được sử dụng hiện tại
        """
        win = tk.Toplevel(self.root)
        win.title("Available Models")
        win.geometry("500x400")
        win.configure(bg=self.bg_color)

        # Tiêu đề
        title = tk.Label(
            win,
            text="AVAILABLE FACE RECOGNITION MODELS",
            font=("Arial", 14, "bold"),
            bg=self.primary_color,
            fg="white",
            pady=10
        )
        title.pack(fill=tk.X)

        # Khung nội dung
        content = tk.Frame(win, bg=self.bg_color)
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Hiển thị từng mô hình
        for i, model in enumerate(models, 1):
            marker = " (current)" if model == current else ""  # Đánh dấu mô hình hiện tại
            model_text = f"{i}. {model}{marker}"

            # Làm nổi bật mô hình hiện tại bằng màu khác
            if model == current:
                bg_color = self.success_color
                fg_color = "white"
            else:
                bg_color = self.bg_color
                fg_color = "#333333"

            lbl = tk.Label(
                content,
                text=model_text,
                font=("Arial", 11),
                bg=bg_color,
                fg=fg_color,
                anchor="w",
                padx=10,
                pady=8
            )
            lbl.pack(fill=tk.X, pady=2)

        # Nút đóng
        close_btn = tk.Button(
            win,
            text="Close",
            command=win.destroy,
            bg=self.primary_color,
            fg="white",
            font=("Arial", 10),
            cursor="hand2",
            padx=20,
            pady=5
        )
        close_btn.pack(pady=10)

    def show_processing(self, message: str = "Processing... Please wait."):
        """
        Hiển thị thông báo đang xử lý

        Args:
            message: Thông điệp xử lý
        """
        # Tạo cửa sổ thông tin đơn giản
        self.display_info(message)

