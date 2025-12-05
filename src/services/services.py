"""
Service layer for business logic
"""
import os
import shutil
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import cv2
import numpy as np

from src.models.models import Student, AttendanceRecord, FaceRecognitionResult
from src.repositories.repositories import StudentRepository, AttendanceRepository
from src.strategies.face_recognition_strategy import FaceRecognitionContext
from src.factories.factory import FaceRecognitionStrategyFactory
from src.config.config import config


class StudentService:
    """Service for managing students"""

    def __init__(self):
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

        Args:
            student_id: Unique student ID
            full_name: Student's full name
            class_name: Class name
            email: Student's email (optional)
            image_path: Path to student's face image (optional, for single image)
            image_paths: List of paths to student's face images (optional, for multiple images)

        Returns:
            Created Student object
        """
        # Create student directory
        student_dir = os.path.join(config.STUDENT_DATABASE_PATH, student_id)
        os.makedirs(student_dir, exist_ok=True)

        face_encoding_path = None

        # Handle multiple images (preferred method)
        if image_paths and len(image_paths) > 0:
            # Copy all images to student directory
            for idx, img_path in enumerate(image_paths):
                if os.path.exists(img_path):
                    ext = os.path.splitext(img_path)[1]
                    dest_path = os.path.join(student_dir, f"{student_id}_{idx}{ext}")
                    shutil.copy(img_path, dest_path)
                    # Use first image as primary encoding path
                    if idx == 0:
                        face_encoding_path = dest_path
        # Handle single image (backward compatibility)
        elif image_path and os.path.exists(image_path):
            ext = os.path.splitext(image_path)[1]
            dest_path = os.path.join(student_dir, f"{student_id}_0{ext}")
            shutil.copy(image_path, dest_path)
            face_encoding_path = dest_path

        # Create student entity
        student = Student(
            student_id=student_id,
            full_name=full_name,
            class_name=class_name,
            email=email,
            face_encoding_path=face_encoding_path
        )

        return self.repository.create(student)

    def add_student_face_image(self, student_id: str, image_path: str = None, image_paths: List[str] = None) -> Student:
        """
        Add or update face image(s) for a student

        Args:
            student_id: Student ID
            image_path: Path to a single face image (optional)
            image_paths: List of paths to face images (optional)

        Returns:
            Updated Student object
        """
        student = self.repository.get_by_id(student_id)
        if not student:
            raise ValueError(f"Student {student_id} not found")

        student_dir = os.path.join(config.STUDENT_DATABASE_PATH, student_id)
        os.makedirs(student_dir, exist_ok=True)

        face_encoding_path = None

        # Handle multiple images
        if image_paths and len(image_paths) > 0:
            for idx, img_path in enumerate(image_paths):
                if os.path.exists(img_path):
                    ext = os.path.splitext(img_path)[1]
                    dest_path = os.path.join(student_dir, f"{student_id}_{idx}{ext}")
                    shutil.copy(img_path, dest_path)
                    if idx == 0:
                        face_encoding_path = dest_path
        # Handle single image
        elif image_path and os.path.exists(image_path):
            ext = os.path.splitext(image_path)[1]
            dest_path = os.path.join(student_dir, f"{student_id}_0{ext}")
            shutil.copy(image_path, dest_path)
            face_encoding_path = dest_path

        if face_encoding_path:
            student.face_encoding_path = face_encoding_path
            return self.repository.update(student)

        raise ValueError("No valid image provided")

    def get_student(self, student_id: str) -> Optional[Student]:
        """Get student by ID"""
        return self.repository.get_by_id(student_id)

    def get_all_students(self) -> List[Student]:
        """Get all students"""
        return self.repository.get_all()

    def get_students_by_class(self, class_name: str) -> List[Student]:
        """Get all students in a specific class"""
        return self.repository.get_by_class(class_name)

    def update_student(
        self,
        student_id: str,
        full_name: str = None,
        class_name: str = None,
        email: str = None
    ) -> Student:
        """Update student information"""
        student = self.repository.get_by_id(student_id)
        if not student:
            raise ValueError(f"Student {student_id} not found")

        if full_name:
            student.full_name = full_name
        if class_name:
            student.class_name = class_name
        if email:
            student.email = email

        return self.repository.update(student)

    def delete_student(self, student_id: str) -> bool:
        """Delete a student and their face data"""
        student = self.repository.get_by_id(student_id)
        if not student:
            return False

        # Delete student directory
        student_dir = os.path.join(config.STUDENT_DATABASE_PATH, student_id)
        if os.path.exists(student_dir):
            shutil.rmtree(student_dir)

        return self.repository.delete(student_id)


class AttendanceService:
    """Service for managing attendance"""

    def __init__(self):
        self.repository = AttendanceRepository()
        self.student_repository = StudentRepository()

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

        Args:
            student_id: Student ID
            confidence_score: Recognition confidence score
            model_used: Name of the model used for recognition
            status: Attendance status (present, late, absent)
            notes: Additional notes

        Returns:
            Created AttendanceRecord
        """
        # Check if student exists
        student = self.student_repository.get_by_id(student_id)
        if not student:
            raise ValueError(f"Student {student_id} not found")

        # Check if already marked for today
        today = date.today().strftime("%Y-%m-%d")
        existing = self.repository.get_by_student_and_date(student_id, today)

        if existing:
            raise ValueError(f"Attendance already marked for student {student_id} today")

        # Create attendance record
        attendance = AttendanceRecord(
            student_id=student_id,
            check_in_time=datetime.now(),
            confidence=confidence_score,
            model_used=model_used,
            status=status,
            session_date=today,
            notes=notes
        )

        return self.repository.create(attendance)

    def get_attendance_by_student(self, student_id: str) -> List[AttendanceRecord]:
        """Get all attendance records for a student"""
        return self.repository.get_by_student(student_id)

    def get_attendance_by_date(self, session_date: str) -> List[AttendanceRecord]:
        """Get all attendance records for a specific date"""
        return self.repository.get_by_date(session_date)

    def get_today_attendance(self) -> List[AttendanceRecord]:
        """Get today's attendance records"""
        today = date.today().strftime("%Y-%m-%d")
        return self.repository.get_by_date(today)

    def update_attendance_status(self, record_id: int, status: str, notes: str = None) -> AttendanceRecord:
        """Update attendance status"""
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

        Args:
            session_date: Date for report (default: today)

        Returns:
            Dictionary with attendance statistics
        """
        if session_date is None:
            session_date = date.today().strftime("%Y-%m-%d")

        records = self.repository.get_by_date(session_date)

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
    """Service for face recognition operations"""

    def __init__(self, model_name: str = None):
        if model_name is None:
            model_name = config.DEFAULT_MODEL

        strategy = FaceRecognitionStrategyFactory.create_strategy(model_name)
        self.context = FaceRecognitionContext(strategy)
        self.student_repository = StudentRepository()

    def change_model(self, model_name: str):
        """Change the recognition model"""
        strategy = FaceRecognitionStrategyFactory.create_strategy(model_name)
        self.context.strategy = strategy

    def recognize_student(self, image_path: str) -> FaceRecognitionResult:
        """
        Recognize student from image

        Args:
            image_path: Path to the image containing face

        Returns:
            FaceRecognitionResult object
        """
        try:
            # First, validate that there are students with images in database
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

            # Perform face recognition
            results = self.context.recognize_face(
                image_path=image_path,
                database_path=config.STUDENT_DATABASE_PATH
            )

            model_name = self.context.get_model_name()
            threshold = config.get_threshold(model_name)

            print(f"\n🔍 Recognition Debug:")
            print(f"   Model: {model_name}")
            print(f"   Threshold: {threshold}")
            print(f"   Results found: {len(results) if results else 0}")

            if results and len(results) > 0 and len(results[0]) > 0:
                # Get the best match
                best_match = results[0].iloc[0]
                distance = best_match['distance']
                confidence = 1 - distance

                print(f"   Best match distance: {distance:.4f}")
                print(f"   Confidence: {confidence:.2%}")

                # Extract student_id from identity path
                identity_path = best_match['identity']
                matched_student_id = self._extract_student_id_from_path(identity_path)

                print(f"   Matched ID: {matched_student_id}")

                # STRICT VALIDATION: Check BOTH distance threshold AND minimum confidence
                if distance < threshold and confidence >= config.MIN_CONFIDENCE_FOR_ATTENDANCE:
                    print(f"   ✓ PASS: Distance < {threshold:.4f} AND Confidence >= {config.MIN_CONFIDENCE_FOR_ATTENDANCE:.0%}")

                    if matched_student_id:
                        student = self.student_repository.get_by_id(matched_student_id)

                        if student:
                            # Additional validation: Check if top 3 results are consistent
                            if len(results[0]) > 1:
                                top_matches = results[0].head(3)
                                print(f"   📊 Top 3 matches:")
                                for idx, row in top_matches.iterrows():
                                    match_id = self._extract_student_id_from_path(row['identity'])
                                    match_conf = 1 - row['distance']
                                    print(f"      {idx+1}. {match_id}: {match_conf:.2%} (dist: {row['distance']:.4f})")

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
                print(f"   ✗ No faces detected in database match")
                print(f"   Possible causes:")
                print(f"     - Webcam image quality different from registered images")
                print(f"     - Face angle/expression too different")
                print(f"     - Try switching model (ArcFace works best: 99% accuracy)")
                print(f"     - Consider re-registering with webcam images")

            # No match found
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
        """Extract student ID from file path"""
        # Path format: data/students/STUDENT_ID/STUDENT_ID.ext
        # Normalize path separators (handle both / and \)
        normalized_path = path.replace('\\', '/')
        parts = normalized_path.split('/')

        for i, part in enumerate(parts):
            if part == 'students' and i + 1 < len(parts):
                student_id = parts[i + 1]
                # Debug print
                print(f"   Extracted student_id: {student_id}")
                return student_id

        # Fallback: try to extract from filename
        filename = os.path.basename(path)
        if '_' in filename:
            student_id = filename.split('_')[0]
            print(f"   Extracted student_id from filename: {student_id}")
            return student_id

        return None

    def _validate_database_has_images(self) -> bool:
        """
        Validate that database has at least one student with images
        Also prints warning for students without images

        Returns:
            True if at least one student has images, False otherwise
        """
        students_path = config.STUDENT_DATABASE_PATH
        if not os.path.exists(students_path):
            return False

        has_images = False
        students_without_images = []

        # Check each student directory
        for student_id in os.listdir(students_path):
            student_dir = os.path.join(students_path, student_id)

            # Skip if not a directory
            if not os.path.isdir(student_dir):
                continue

            # Count image files
            image_files = [f for f in os.listdir(student_dir)
                          if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]

            if len(image_files) == 0:
                students_without_images.append(student_id)
            else:
                has_images = True

        # Print warning for students without images
        if students_without_images:
            print(f"\n⚠️  WARNING: Students without face images:")
            for sid in students_without_images:
                print(f"   - {sid} (0 images) - Cannot be recognized!")
            print(f"   Please add images for these students using option 2 in menu.\n")

        return has_images

    def verify_student(self, image_path: str, student_id: str) -> Dict[str, Any]:
        """
        Verify if image matches a specific student

        Args:
            image_path: Path to the image to verify
            student_id: Student ID to verify against

        Returns:
            Verification result dictionary
        """
        student = self.student_repository.get_by_id(student_id)
        if not student or not student.face_encoding_path:
            return {
                'verified': False,
                'message': 'Student not found or no face image registered'
            }

        try:
            result = self.context.verify_face(image_path, student.face_encoding_path)
            return result
        except Exception as e:
            return {
                'verified': False,
                'message': f'Error: {str(e)}'
            }

    def get_available_models(self) -> List[str]:
        """Get list of available recognition models"""
        return FaceRecognitionStrategyFactory.get_available_models()

