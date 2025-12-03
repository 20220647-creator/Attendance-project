"""
Tkinter GUI View layer for Face Recognition Attendance System
"""
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from src.models.models import Student, AttendanceRecord
import threading


class TkinterView:
    """Tkinter-based GUI view"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Face Recognition Attendance System")
        self.root.geometry("900x700")

        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Colors
        self.bg_color = "#f0f0f0"
        self.primary_color = "#2196F3"
        self.success_color = "#4CAF50"
        self.error_color = "#f44336"
        self.warning_color = "#FF9800"

        self.root.configure(bg=self.bg_color)

        # Input callback for getting user input
        self._input_callback = None
        self._input_result = None

    def display_menu(self, callback: Callable[[str], None]):
        """Display main menu as buttons"""
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # Title
        title_frame = tk.Frame(self.root, bg=self.primary_color, height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)

        title_label = tk.Label(
            title_frame,
            text="FACE RECOGNITION ATTENDANCE SYSTEM",
            font=("Arial", 16, "bold"),
            bg=self.primary_color,
            fg="white"
        )
        title_label.pack(pady=15)

        # Main container with scrollbar
        main_container = tk.Frame(self.root, bg=self.bg_color)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        canvas = tk.Canvas(main_container, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.bg_color)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Menu sections
        sections = [
            ("STUDENT MANAGEMENT", [
                ("1", "Register new student", self.primary_color),
                ("2", "Add face image to student", self.primary_color),
                ("3", "View student information", self.primary_color),
                ("4", "List all students", self.primary_color),
                ("5", "Update student information", self.primary_color),
                ("6", "Delete student", self.error_color),
            ]),
            ("ATTENDANCE", [
                ("7", "Take attendance from image", self.success_color),
                ("8", "Take attendance from webcam", self.success_color),
                ("9", "View today's attendance", self.primary_color),
                ("10", "View attendance by date", self.primary_color),
                ("11", "View student attendance history", self.primary_color),
                ("12", "Generate attendance report", self.primary_color),
            ]),
            ("SETTINGS", [
                ("13", "Change recognition model", self.warning_color),
                ("14", "View available models", self.primary_color),
            ]),
            ("OTHER", [
                ("15", "Test face recognition", self.warning_color),
                ("0", "Exit", self.error_color),
            ])
        ]

        for section_name, buttons in sections:
            # Section header
            section_frame = tk.LabelFrame(
                scrollable_frame,
                text=section_name,
                font=("Arial", 11, "bold"),
                bg=self.bg_color,
                fg="#333333"
            )
            section_frame.pack(fill=tk.X, pady=10)

            # Buttons
            for choice, text, color in buttons:
                btn = tk.Button(
                    section_frame,
                    text=f"{choice}. {text}",
                    font=("Arial", 10),
                    bg=color,
                    fg="white",
                    activebackground=color,
                    activeforeground="white",
                    cursor="hand2",
                    relief=tk.FLAT,
                    padx=20,
                    pady=10,
                    command=lambda c=choice: callback(c)
                )
                btn.pack(fill=tk.X, padx=10, pady=5)

    def display_success(self, message: str):
        """Display success message"""
        messagebox.showinfo("Success", message)

    def display_error(self, message: str):
        """Display error message"""
        messagebox.showerror("Error", message)

    def display_info(self, message: str):
        """Display information message"""
        messagebox.showinfo("Information", message)

    def display_warning(self, message: str):
        """Display warning message"""
        messagebox.showwarning("Warning", message)

    def get_input(self, prompt: str) -> str:
        """Get user input via dialog"""
        result = simpledialog.askstring("Input", prompt, parent=self.root)
        return result if result else ""

    def get_choice(self) -> str:
        """Get menu choice (not used in GUI mode)"""
        return ""

    def pause(self):
        """Pause (not needed in GUI mode)"""
        pass

    def display_student(self, student: Student):
        """Display student information in a new window"""
        win = tk.Toplevel(self.root)
        win.title("Student Information")
        win.geometry("500x400")
        win.configure(bg=self.bg_color)

        # Title
        title = tk.Label(
            win,
            text="STUDENT INFORMATION",
            font=("Arial", 14, "bold"),
            bg=self.primary_color,
            fg="white",
            pady=10
        )
        title.pack(fill=tk.X)

        # Content frame
        content = tk.Frame(win, bg=self.bg_color)
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Student details
        details = [
            ("Student ID:", student.student_id),
            ("Full Name:", student.full_name),
            ("Class:", student.class_name),
            ("Email:", student.email or "N/A"),
            ("Face Image:", "Registered" if student.face_encoding_path else "Not registered"),
            ("Created:", student.created_at.strftime('%Y-%m-%d %H:%M:%S'))
        ]

        for i, (label, value) in enumerate(details):
            lbl = tk.Label(content, text=label, font=("Arial", 10, "bold"), bg=self.bg_color, anchor="w")
            lbl.grid(row=i, column=0, sticky="w", pady=5, padx=5)

            val = tk.Label(content, text=value, font=("Arial", 10), bg=self.bg_color, anchor="w")
            val.grid(row=i, column=1, sticky="w", pady=5, padx=5)

        # Close button
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

    def display_students_list(self, students: List[Student]):
        """Display list of students in a new window"""
        win = tk.Toplevel(self.root)
        win.title("Students List")
        win.geometry("900x500")
        win.configure(bg=self.bg_color)

        # Title
        title = tk.Label(
            win,
            text=f"ALL STUDENTS (Total: {len(students)})",
            font=("Arial", 14, "bold"),
            bg=self.primary_color,
            fg="white",
            pady=10
        )
        title.pack(fill=tk.X)

        if not students:
            msg = tk.Label(win, text="No students found.", font=("Arial", 12), bg=self.bg_color)
            msg.pack(pady=50)
            return

        # Treeview
        frame = tk.Frame(win, bg=self.bg_color)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tree = ttk.Treeview(
            frame,
            columns=("ID", "Name", "Class", "Email", "Face"),
            show="headings",
            height=15
        )

        # Configure columns
        tree.heading("ID", text="Student ID")
        tree.heading("Name", text="Full Name")
        tree.heading("Class", text="Class")
        tree.heading("Email", text="Email")
        tree.heading("Face", text="Face")

        tree.column("ID", width=120)
        tree.column("Name", width=200)
        tree.column("Class", width=150)
        tree.column("Email", width=200)
        tree.column("Face", width=80)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        # Add data
        for student in students:
            face_status = "✓" if student.face_encoding_path else "✗"
            email = student.email if student.email else "N/A"
            tree.insert("", "end", values=(
                student.student_id,
                student.full_name,
                student.class_name,
                email,
                face_status
            ))

        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Close button
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
        """Display list of attendance records"""
        win = tk.Toplevel(self.root)
        title_text = f"Attendance Records - {date}" if date else "Attendance Records"
        win.title(title_text)
        win.geometry("900x500")
        win.configure(bg=self.bg_color)

        # Title
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

        # Configure columns
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

        # Add data
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

        # Close button
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
        """Display attendance report"""
        win = tk.Toplevel(self.root)
        win.title("Attendance Report")
        win.geometry("500x350")
        win.configure(bg=self.bg_color)

        # Title
        title = tk.Label(
            win,
            text=f"ATTENDANCE REPORT - {report['date']}",
            font=("Arial", 14, "bold"),
            bg=self.primary_color,
            fg="white",
            pady=10
        )
        title.pack(fill=tk.X)

        # Content frame
        content = tk.Frame(win, bg=self.bg_color)
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Report details
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

        # Close button
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
        """Display face recognition result"""
        win = tk.Toplevel(self.root)
        win.title("Recognition Result")
        win.geometry("500x350")
        win.configure(bg=self.bg_color)

        if result.get('recognized', False):
            # Recognized
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

            # Content
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
            # Not recognized
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

        # Close button
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
        """Display available models in a selection window"""
        win = tk.Toplevel(self.root)
        win.title("Available Models")
        win.geometry("500x400")
        win.configure(bg=self.bg_color)

        # Title
        title = tk.Label(
            win,
            text="AVAILABLE FACE RECOGNITION MODELS",
            font=("Arial", 14, "bold"),
            bg=self.primary_color,
            fg="white",
            pady=10
        )
        title.pack(fill=tk.X)

        # Content frame
        content = tk.Frame(win, bg=self.bg_color)
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        for i, model in enumerate(models, 1):
            marker = " (current)" if model == current else ""
            model_text = f"{i}. {model}{marker}"

            # Highlight current model
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

        # Close button
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
        """Show processing message in a non-blocking way"""
        # Create a simple info window
        self.display_info(message)

