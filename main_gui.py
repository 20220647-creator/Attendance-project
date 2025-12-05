# -*- coding: utf-8 -*-
"""
Main GUI application entry point
Face Recognition Attendance System with Tkinter Interface
"""
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import date

# Fix encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

from src.controllers.controllers import (
    StudentController,
    AttendanceController,
    FaceRecognitionController,
    DataAugmentationController
)
from src.views.tkinter_views import TkinterView
from src.utils.utils import CameraUtility, ImageValidator
from src.config.config import config


class AttendanceApplicationGUI:
    """Main GUI application class"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.student_controller = StudentController()
        self.attendance_controller = AttendanceController()
        self.face_controller = FaceRecognitionController()
        self.augmentation_controller = DataAugmentationController()
        self.view = TkinterView(root)
        self.running = True
        self.current_model = config.DEFAULT_MODEL

        # Show initial info
        self.view.display_info(f"System initialized with model: {self.current_model}")

        # Start main menu
        self.show_menu()

    def show_menu(self):
        """Show main menu"""
        self.view.display_menu(self.handle_choice)

    def handle_choice(self, choice: str):
        """Handle user menu choice"""
        handlers = {
            '1': self.register_student,
            '2': self.add_face_image,
            '3': self.view_student,
            '4': self.list_students,
            '5': self.update_student,
            '6': self.delete_student,
            '7': self.take_attendance_image,
            '8': self.take_attendance_webcam,
            '9': self.view_today_attendance,
            '10': self.view_attendance_by_date,
            '11': self.view_student_history,
            '12': self.generate_report,
            '13': self.change_model,
            '14': self.view_models,
            '15': self.test_recognition,
            '16': self.augment_student_data,
            '17': self.augment_all_students_data,
            '18': self.clean_augmented_data,
            '0': self.exit_application
        }

        handler = handlers.get(choice)
        if handler:
            try:
                handler()
            except Exception as e:
                self.view.display_error(f"Error: {str(e)}")
                import traceback
                traceback.print_exc()
        else:
            self.view.display_error("Invalid choice. Please try again.")

    def register_student(self):
        """Register a new student"""
        student_id = self.view.get_input("Enter Student ID")
        if not student_id:
            self.view.display_error("Student ID cannot be empty")
            return

        full_name = self.view.get_input("Enter Full Name")
        if not full_name:
            self.view.display_error("Full name cannot be empty")
            return

        class_name = self.view.get_input("Enter Class Name")
        email = self.view.get_input("Enter Email (optional)")

        # Ask if they want to add face images
        add_images = messagebox.askyesno("Add Images", "Add face images now?")
        image_paths = None

        if add_images:
            # Ask for method
            choice = messagebox.askquestion(
                "Image Source",
                "Capture from webcam?\n\nYes = Webcam (multiple samples)\nNo = Select file",
                icon='question'
            )

            if choice == 'yes':
                # Multiple samples from webcam
                self.view.display_info(f"Will capture {config.NUM_FACE_SAMPLES} face samples for better recognition")

                student_dir = os.path.join(config.STUDENT_DATABASE_PATH, student_id)
                image_paths = CameraUtility.capture_multiple_from_webcam(
                    save_dir=student_dir,
                    student_id=student_id,
                    num_samples=config.NUM_FACE_SAMPLES,
                    delay=config.SAMPLE_CAPTURE_DELAY
                )

                if not image_paths:
                    self.view.display_warning("No images captured")
            else:
                # Single file mode
                image_path = filedialog.askopenfilename(
                    title="Select face image",
                    filetypes=[("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")]
                )

                if image_path:
                    is_valid, message = ImageValidator.validate_face_image(image_path)
                    if is_valid:
                        image_paths = [image_path]
                    else:
                        self.view.display_error(message)

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

    def add_face_image(self):
        """Add face image to existing student"""
        student_id = self.view.get_input("Enter Student ID")
        if not student_id:
            return

        # Ask for method
        choice = messagebox.askquestion(
            "Image Source",
            "Capture from webcam?\n\nYes = Webcam (multiple samples)\nNo = Select file",
            icon='question'
        )

        image_paths = None
        if choice == 'yes':
            # Multiple samples from webcam
            self.view.display_info(f"Will capture {config.NUM_FACE_SAMPLES} face samples")

            student_dir = os.path.join(config.STUDENT_DATABASE_PATH, student_id)
            image_paths = CameraUtility.capture_multiple_from_webcam(
                save_dir=student_dir,
                student_id=student_id,
                num_samples=config.NUM_FACE_SAMPLES,
                delay=config.SAMPLE_CAPTURE_DELAY
            )
        else:
            # Single file mode
            image_path = filedialog.askopenfilename(
                title="Select face image",
                filetypes=[("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")]
            )

            if image_path:
                is_valid, message = ImageValidator.validate_face_image(image_path)
                if is_valid:
                    image_paths = [image_path]
                else:
                    self.view.display_error(message)
                    return

        if image_paths:
            result = self.student_controller.add_face_image(student_id, image_paths=image_paths)

            if result['success']:
                self.view.display_success(result['message'])
            else:
                self.view.display_error(result['message'])
        else:
            self.view.display_error("No image provided")

    def view_student(self):
        """View student information"""
        student_id = self.view.get_input("Enter Student ID")
        if not student_id:
            return

        result = self.student_controller.get_student_info(student_id)

        if result['success']:
            self.view.display_student(result['student'])
        else:
            self.view.display_error(result['message'])

    def list_students(self):
        """List all students"""
        result = self.student_controller.list_all_students()

        if result['success']:
            self.view.display_students_list(result['students'])
        else:
            self.view.display_error(result['message'])

    def update_student(self):
        """Update student information"""
        student_id = self.view.get_input("Enter Student ID")
        if not student_id:
            return

        # First, show current info
        result = self.student_controller.get_student_info(student_id)
        if not result['success']:
            self.view.display_error(result['message'])
            return

        self.view.display_student(result['student'])

        messagebox.showinfo("Update", "Enter new values (leave empty to keep current)")

        full_name = self.view.get_input("Full Name (leave empty to keep current)")
        class_name = self.view.get_input("Class Name (leave empty to keep current)")
        email = self.view.get_input("Email (leave empty to keep current)")

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

    def delete_student(self):
        """Delete a student"""
        student_id = self.view.get_input("Enter Student ID")
        if not student_id:
            return

        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete student {student_id}?\n\nThis action cannot be undone."
        )

        if confirm:
            result = self.student_controller.delete_student(student_id)

            if result['success']:
                self.view.display_success(result['message'])
            else:
                self.view.display_error(result['message'])

    def take_attendance_image(self):
        """Take attendance from image file"""
        image_path = filedialog.askopenfilename(
            title="Select image for attendance",
            filetypes=[("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")]
        )

        if not image_path:
            return

        self.view.show_processing("Processing... Please wait.")

        result = self.attendance_controller.take_attendance_from_image(
            image_path=image_path,
            model_name=self.current_model
        )

        if result['success']:
            message = f"{result['message']}\n\n"
            message += f"Student: {result['student_name']} ({result['student_id']})\n"
            message += f"Confidence: {result['confidence']:.2%}\n"
            message += f"Model: {result['model_used']}"
            self.view.display_success(message)
        else:
            self.view.display_error(result['message'])

    def take_attendance_webcam(self):
        """Take attendance from webcam"""
        temp_path = os.path.join(config.ATTENDANCE_LOG_PATH, f"temp_capture_{date.today()}.jpg")

        image_path = CameraUtility.capture_from_webcam(temp_path)

        if image_path:
            self.view.show_processing("Processing... Please wait.")

            result = self.attendance_controller.take_attendance_from_image(
                image_path=image_path,
                model_name=self.current_model
            )

            if result['success']:
                message = f"{result['message']}\n\n"
                message += f"Student: {result['student_name']} ({result['student_id']})\n"
                message += f"Confidence: {result['confidence']:.2%}\n"
                message += f"Model: {result['model_used']}"
                self.view.display_success(message)

                # Clean up temp file on success
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            else:
                self.view.display_error(result['message'])
        else:
            self.view.display_error("No image captured")

    def view_today_attendance(self):
        """View today's attendance"""
        result = self.attendance_controller.get_today_attendance()

        if result['success']:
            self.view.display_attendance_list(result['records'], result['date'])
        else:
            self.view.display_error(result['message'])

    def view_attendance_by_date(self):
        """View attendance by date"""
        session_date = self.view.get_input("Enter date (YYYY-MM-DD) or leave empty for today")

        if not session_date:
            session_date = None

        result = self.attendance_controller.get_attendance_by_date(session_date)

        if result['success']:
            self.view.display_attendance_list(result['records'], result['date'])
        else:
            self.view.display_error(result['message'])

    def view_student_history(self):
        """View student attendance history"""
        student_id = self.view.get_input("Enter Student ID")
        if not student_id:
            return

        result = self.attendance_controller.get_student_attendance_history(student_id)

        if result['success']:
            self.view.display_attendance_list(result['records'])
        else:
            self.view.display_error(result['message'])

    def generate_report(self):
        """Generate attendance report"""
        session_date = self.view.get_input("Enter date (YYYY-MM-DD) or leave empty for today")

        if not session_date:
            session_date = None

        result = self.attendance_controller.generate_report(session_date)

        if result['success']:
            self.view.display_attendance_report(result['report'])
            # Also show detailed list
            self.view.display_attendance_list(result['report']['records'], result['report']['date'])
        else:
            self.view.display_error(result['message'])

    def change_model(self):
        """Change face recognition model"""
        result = self.attendance_controller.get_available_models()

        if result['success']:
            self.view.display_models_list(result['models'], self.current_model)

            model_choice = self.view.get_input("Enter model number or name")
            if not model_choice:
                return

            # Check if it's a number
            try:
                model_idx = int(model_choice) - 1
                if 0 <= model_idx < len(result['models']):
                    model_name = result['models'][model_idx]
                else:
                    self.view.display_error("Invalid model number")
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

    def view_models(self):
        """View available models"""
        result = self.attendance_controller.get_available_models()

        if result['success']:
            self.view.display_models_list(result['models'], self.current_model)
        else:
            self.view.display_error(result['message'])

    def test_recognition(self):
        """Test face recognition without marking attendance"""
        choice = messagebox.askquestion(
            "Image Source",
            "Capture from webcam?\n\nYes = Webcam\nNo = Select file",
            icon='question'
        )

        image_path = None
        if choice == 'yes':
            temp_path = os.path.join(config.ATTENDANCE_LOG_PATH, "test_capture.jpg")
            image_path = CameraUtility.capture_from_webcam(temp_path)
        else:
            image_path = filedialog.askopenfilename(
                title="Select image to test",
                filetypes=[("Image files", "*.jpg *.jpeg *.png"), ("All files", "*.*")]
            )

        if image_path and os.path.exists(image_path):
            self.view.show_processing("Processing... Please wait.")

            result = self.face_controller.recognize_face(image_path, self.current_model)

            if result['success']:
                self.view.display_recognition_result(result)
            else:
                self.view.display_error(result['message'])
        else:
            self.view.display_error("No image provided or file not found")

    def augment_student_data(self):
        """Augment data for a single student"""
        student_id = self.view.get_input("Enter Student ID")
        if not student_id:
            return

        # Ask for number of augmented images
        num_str = self.view.get_input("Number of augmented images per original (default: 5)")
        try:
            num_augmented = int(num_str) if num_str else 5
            if num_augmented < 1 or num_augmented > 20:
                self.view.display_error("Number must be between 1 and 20")
                return
        except ValueError:
            self.view.display_error("Invalid number")
            return

        # Confirm
        confirm = messagebox.askyesno(
            "Confirm Augmentation",
            f"This will create {num_augmented} augmented images per original image for student {student_id}.\n\n"
            "This improves recognition accuracy!\n\nContinue?"
        )

        if not confirm:
            return

        self.view.show_processing("Augmenting data... Please wait.")

        result = self.augmentation_controller.augment_student(student_id, num_augmented)

        if result['success']:
            message = f"{result['message']}\n\n"
            message += f"Original images: {result['original_images']}\n"
            message += f"Augmented images: {result['augmented_images']}\n"
            message += f"Total images now: {result['total_images']}"
            self.view.display_success(message)
        else:
            self.view.display_error(result['message'])

    def augment_all_students_data(self):
        """Augment data for all students"""
        # Ask for number of augmented images
        num_str = self.view.get_input("Number of augmented images per original (default: 5)")
        try:
            num_augmented = int(num_str) if num_str else 5
            if num_augmented < 1 or num_augmented > 20:
                self.view.display_error("Number must be between 1 and 20")
                return
        except ValueError:
            self.view.display_error("Invalid number")
            return

        # Confirm
        confirm = messagebox.askyesno(
            "Confirm Mass Augmentation",
            f"This will augment data for ALL students!\n\n"
            f"Creating {num_augmented} images per original.\n"
            "This may take several minutes.\n\n"
            "Continue?"
        )

        if not confirm:
            return

        self.view.show_processing("Augmenting all students... This may take a while.")

        result = self.augmentation_controller.augment_all_students(num_augmented)

        if result['success']:
            stats = result['stats']
            message = f"{result['message']}\n\n"
            message += f"Students processed: {stats['students_processed']}\n"
            message += f"Original images: {stats['original_images']}\n"
            message += f"Augmented images: {stats['augmented_images']}\n"
            message += f"Total images now: {stats['original_images'] + stats['augmented_images']}"

            if stats['errors']:
                message += f"\n\nErrors: {len(stats['errors'])}"

            self.view.display_success(message)
        else:
            self.view.display_error(result['message'])

    def clean_augmented_data(self):
        """Clean augmented images"""
        # Ask for scope
        choice = messagebox.askquestion(
            "Clean Scope",
            "Clean all students?\n\nYes = All students\nNo = Single student",
            icon='question'
        )

        student_id = None
        if choice == 'no':
            student_id = self.view.get_input("Enter Student ID")
            if not student_id:
                return

        # Confirm
        scope_text = "ALL STUDENTS" if not student_id else f"student {student_id}"
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"This will delete all augmented images for {scope_text}.\n\n"
            "Original images will NOT be affected.\n\n"
            "Continue?"
        )

        if not confirm:
            return

        result = self.augmentation_controller.clean_augmented_images(student_id)

        if result['success']:
            self.view.display_success(f"{result['message']}\n\nDeleted: {result['deleted_count']} files")
        else:
            self.view.display_error(result['message'])

    def exit_application(self):
        """Exit the application"""
        confirm = messagebox.askyesno(
            "Exit",
            "Are you sure you want to exit?"
        )
        if confirm:
            self.root.quit()


def main():
    """Main entry point"""
    try:
        root = tk.Tk()
        app = AttendanceApplicationGUI(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Fatal Error", f"Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

