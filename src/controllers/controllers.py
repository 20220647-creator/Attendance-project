"""
Controller layer for handling user interactions (MVC Pattern)
"""
from typing import Optional, Dict, Any, List
from datetime import date
import os

from src.services.services import StudentService, AttendanceService, FaceRecognitionService
from src.models.models import Student, AttendanceRecord, FaceRecognitionResult


class StudentController:
    """Controller for student-related operations"""

    def __init__(self):
        self.service = StudentService()

    def register_new_student(
        self,
        student_id: str,
        full_name: str,
        class_name: str,
        email: str = None,
        image_path: str = None,
        image_paths: List[str] = None
    ) -> Dict[str, Any]:
        """
        Register a new student

        Args:
            student_id: Student ID
            full_name: Full name
            class_name: Class name
            email: Email (optional)
            image_path: Single image path (optional)
            image_paths: Multiple image paths (optional)

        Returns:
            Dictionary with status and message
        """
        try:
            student = self.service.register_student(
                student_id=student_id,
                full_name=full_name,
                class_name=class_name,
                email=email,
                image_path=image_path,
                image_paths=image_paths
            )
            num_images = len(image_paths) if image_paths else (1 if image_path else 0)
            message = f'Student {student_id} registered successfully'
            if num_images > 0:
                message += f' with {num_images} face sample(s)'
            return {
                'success': True,
                'message': message,
                'student': student
            }
        except ValueError as e:
            return {
                'success': False,
                'message': str(e)
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error registering student: {str(e)}'
            }

    def add_face_image(self, student_id: str, image_path: str = None, image_paths: List[str] = None) -> Dict[str, Any]:
        """Add or update face image(s) for a student"""
        try:
            # Check if any images provided
            if not image_path and not image_paths:
                return {
                    'success': False,
                    'message': 'No image provided'
                }

            # Validate single image
            if image_path and not os.path.exists(image_path):
                return {
                    'success': False,
                    'message': 'Image file not found'
                }

            # Validate multiple images
            if image_paths:
                for img_path in image_paths:
                    if not os.path.exists(img_path):
                        return {
                            'success': False,
                            'message': f'Image file not found: {img_path}'
                        }

            student = self.service.add_student_face_image(student_id, image_path, image_paths)
            num_images = len(image_paths) if image_paths else 1
            return {
                'success': True,
                'message': f'{num_images} face image(s) added for student {student_id}',
                'student': student
            }
        except ValueError as e:
            return {
                'success': False,
                'message': str(e)
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error adding face image: {str(e)}'
            }

    def get_student_info(self, student_id: str) -> Dict[str, Any]:
        """Get student information"""
        try:
            student = self.service.get_student(student_id)
            if student:
                return {
                    'success': True,
                    'student': student
                }
            else:
                return {
                    'success': False,
                    'message': f'Student {student_id} not found'
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving student: {str(e)}'
            }

    def list_all_students(self) -> Dict[str, Any]:
        """List all registered students"""
        try:
            students = self.service.get_all_students()
            return {
                'success': True,
                'count': len(students),
                'students': students
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error listing students: {str(e)}'
            }

    def list_students_by_class(self, class_name: str) -> Dict[str, Any]:
        """List all students in a class"""
        try:
            students = self.service.get_students_by_class(class_name)
            return {
                'success': True,
                'count': len(students),
                'class': class_name,
                'students': students
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error listing students: {str(e)}'
            }

    def update_student_info(
        self,
        student_id: str,
        full_name: str = None,
        class_name: str = None,
        email: str = None
    ) -> Dict[str, Any]:
        """Update student information"""
        try:
            student = self.service.update_student(
                student_id=student_id,
                full_name=full_name,
                class_name=class_name,
                email=email
            )
            return {
                'success': True,
                'message': f'Student {student_id} updated successfully',
                'student': student
            }
        except ValueError as e:
            return {
                'success': False,
                'message': str(e)
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error updating student: {str(e)}'
            }

    def delete_student(self, student_id: str) -> Dict[str, Any]:
        """Delete a student"""
        try:
            success = self.service.delete_student(student_id)
            if success:
                return {
                    'success': True,
                    'message': f'Student {student_id} deleted successfully'
                }
            else:
                return {
                    'success': False,
                    'message': f'Student {student_id} not found'
                }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error deleting student: {str(e)}'
            }


class AttendanceController:
    """Controller for attendance-related operations"""

    def __init__(self):
        self.service = AttendanceService()
        self.recognition_service = FaceRecognitionService()

    def take_attendance_from_image(
        self,
        image_path: str,
        model_name: str = None,
        status: str = 'present'
    ) -> Dict[str, Any]:
        """
        Take attendance by recognizing face from image

        Args:
            image_path: Path to the image
            model_name: Recognition model to use (optional)
            status: Attendance status

        Returns:
            Dictionary with result
        """
        try:
            if not os.path.exists(image_path):
                return {
                    'success': False,
                    'message': 'Image file not found'
                }

            # Change model if specified
            if model_name:
                self.recognition_service.change_model(model_name)

            # Recognize face
            result = self.recognition_service.recognize_student(image_path)

            if not result.success:
                return {
                    'success': False,
                    'message': 'No student recognized in the image',
                    'recognition_result': result
                }

            # Mark attendance
            try:
                attendance = self.service.mark_attendance(
                    student_id=result.student_id,
                    confidence_score=result.confidence,
                    model_used=result.model_used,
                    status=status
                )

                return {
                    'success': True,
                    'message': f'Attendance marked for {result.student_name}',
                    'student_id': result.student_id,
                    'student_name': result.student_name,
                    'confidence': result.confidence,
                    'model_used': result.model_used,
                    'attendance': attendance
                }
            except ValueError as e:
                return {
                    'success': False,
                    'message': str(e),
                    'recognition_result': result
                }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error taking attendance: {str(e)}'
            }

    def get_student_attendance_history(self, student_id: str) -> Dict[str, Any]:
        """Get attendance history for a student"""
        try:
            records = self.service.get_attendance_by_student(student_id)
            return {
                'success': True,
                'student_id': student_id,
                'count': len(records),
                'records': records
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving attendance: {str(e)}'
            }

    def get_attendance_by_date(self, session_date: str = None) -> Dict[str, Any]:
        """Get attendance records for a specific date"""
        try:
            if session_date is None:
                session_date = date.today().strftime("%Y-%m-%d")

            records = self.service.get_attendance_by_date(session_date)
            return {
                'success': True,
                'date': session_date,
                'count': len(records),
                'records': records
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving attendance: {str(e)}'
            }

    def get_today_attendance(self) -> Dict[str, Any]:
        """Get today's attendance"""
        try:
            records = self.service.get_today_attendance()
            return {
                'success': True,
                'date': date.today().strftime("%Y-%m-%d"),
                'count': len(records),
                'records': records
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving attendance: {str(e)}'
            }

    def update_attendance_status(
        self,
        record_id: int,
        status: str,
        notes: str = None
    ) -> Dict[str, Any]:
        """Update attendance status"""
        try:
            record = self.service.update_attendance_status(record_id, status, notes)
            return {
                'success': True,
                'message': 'Attendance status updated',
                'record': record
            }
        except ValueError as e:
            return {
                'success': False,
                'message': str(e)
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error updating attendance: {str(e)}'
            }

    def generate_report(self, session_date: str = None) -> Dict[str, Any]:
        """Generate attendance report"""
        try:
            report = self.service.generate_attendance_report(session_date)
            return {
                'success': True,
                'report': report
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error generating report: {str(e)}'
            }

    def change_recognition_model(self, model_name: str) -> Dict[str, Any]:
        """Change the face recognition model"""
        try:
            self.recognition_service.change_model(model_name)
            return {
                'success': True,
                'message': f'Model changed to {model_name}'
            }
        except ValueError as e:
            return {
                'success': False,
                'message': str(e)
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error changing model: {str(e)}'
            }

    def get_available_models(self) -> Dict[str, Any]:
        """Get list of available recognition models"""
        try:
            models = self.recognition_service.get_available_models()
            return {
                'success': True,
                'models': models
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error retrieving models: {str(e)}'
            }


class FaceRecognitionController:
    """Controller for face recognition operations"""

    def __init__(self):
        self.service = FaceRecognitionService()

    def recognize_face(self, image_path: str, model_name: str = None) -> Dict[str, Any]:
        """Recognize face in image"""
        try:
            if not os.path.exists(image_path):
                return {
                    'success': False,
                    'message': 'Image file not found'
                }

            if model_name:
                self.service.change_model(model_name)

            result = self.service.recognize_student(image_path)

            return {
                'success': True,
                'recognized': result.success,
                'result': result
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error in face recognition: {str(e)}'
            }

    def verify_face(self, image_path: str, student_id: str) -> Dict[str, Any]:
        """Verify if face matches a student"""
        try:
            if not os.path.exists(image_path):
                return {
                    'success': False,
                    'message': 'Image file not found'
                }

            result = self.service.verify_student(image_path, student_id)

            return {
                'success': True,
                'verification': result
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error in face verification: {str(e)}'
            }


class DataAugmentationController:
    """Controller for data augmentation operations"""

    def __init__(self):
        from src.utils.data_augmentation import FaceDataAugmentation, augment_existing_dataset
        from src.config.config import config
        self.augmentor = FaceDataAugmentation()
        self.augment_existing_dataset = augment_existing_dataset
        self.data_dir = config.STUDENT_DATABASE_PATH

    def augment_student(self, student_id: str, num_augmented: int = 5) -> Dict[str, Any]:
        """
        Augment images for a specific student

        Args:
            student_id: Student ID
            num_augmented: Number of augmented images per original image

        Returns:
            Dictionary with results
        """
        try:
            student_dir = os.path.join(self.data_dir, student_id)

            if not os.path.exists(student_dir):
                return {
                    'success': False,
                    'message': f'Student {student_id} not found'
                }

            # Count original images
            original_count = len([f for f in os.listdir(student_dir)
                                 if f.lower().endswith(('.jpg', '.jpeg', '.png'))
                                 and not f.startswith('aug_')])

            if original_count == 0:
                return {
                    'success': False,
                    'message': f'No images found for student {student_id}'
                }

            # Augment
            created = self.augmentor.augment_student_images(
                student_dir,
                num_augmented=num_augmented
            )

            return {
                'success': True,
                'message': f'Created {created} augmented images for {student_id}',
                'student_id': student_id,
                'original_images': original_count,
                'augmented_images': created,
                'total_images': original_count + created
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error augmenting student data: {str(e)}'
            }

    def augment_all_students(self, num_augmented: int = 5) -> Dict[str, Any]:
        """
        Augment images for all students

        Args:
            num_augmented: Number of augmented images per original image

        Returns:
            Dictionary with statistics
        """
        try:
            if not os.path.exists(self.data_dir):
                return {
                    'success': False,
                    'message': f'Data directory not found: {self.data_dir}'
                }

            stats = self.augment_existing_dataset(
                self.data_dir,
                augmentation_per_image=num_augmented
            )

            return {
                'success': True,
                'message': f'Augmented {stats["students_processed"]} students',
                'stats': stats
            }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error augmenting dataset: {str(e)}'
            }

    def clean_augmented_images(self, student_id: str = None) -> Dict[str, Any]:
        """
        Remove all augmented images

        Args:
            student_id: Student ID (None = all students)

        Returns:
            Dictionary with results
        """
        try:
            deleted_count = 0

            if student_id:
                # Clean specific student
                student_dir = os.path.join(self.data_dir, student_id)
                if not os.path.exists(student_dir):
                    return {
                        'success': False,
                        'message': f'Student {student_id} not found'
                    }

                for filename in os.listdir(student_dir):
                    if filename.startswith('aug_'):
                        file_path = os.path.join(student_dir, filename)
                        os.remove(file_path)
                        deleted_count += 1

                return {
                    'success': True,
                    'message': f'Deleted {deleted_count} augmented images for {student_id}',
                    'deleted_count': deleted_count
                }
            else:
                # Clean all students
                for student_folder in os.listdir(self.data_dir):
                    student_dir = os.path.join(self.data_dir, student_folder)
                    if not os.path.isdir(student_dir):
                        continue

                    for filename in os.listdir(student_dir):
                        if filename.startswith('aug_'):
                            file_path = os.path.join(student_dir, filename)
                            os.remove(file_path)
                            deleted_count += 1

                return {
                    'success': True,
                    'message': f'Deleted {deleted_count} augmented images from all students',
                    'deleted_count': deleted_count
                }

        except Exception as e:
            return {
                'success': False,
                'message': f'Error cleaning augmented images: {str(e)}'
            }
