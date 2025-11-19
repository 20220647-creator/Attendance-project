"""
Repository pattern for data access layer
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime, date
from sqlalchemy.exc import IntegrityError

from src.models.models import Student, AttendanceRecord
from src.database.database import db_manager


class IRepository(ABC):
    """Interface for Repository Pattern"""

    @abstractmethod
    def create(self, entity):
        pass

    @abstractmethod
    def get_by_id(self, entity_id):
        pass

    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    def update(self, entity):
        pass

    @abstractmethod
    def delete(self, entity_id):
        pass


class StudentRepository(IRepository):
    """Repository for Student entity"""

    def create(self, student: Student) -> Student:
        """Create a new student"""
        with db_manager.get_session() as session:
            try:
                session.add(student)
                session.flush()
                # Make the object accessible outside session
                session.expunge(student)
                return student
            except IntegrityError:
                raise ValueError(f"Student with ID {student.student_id} already exists")

    def get_by_id(self, student_id: str) -> Optional[Student]:
        """Get student by student_id"""
        with db_manager.get_session() as session:
            student = session.query(Student).filter(Student.student_id == student_id).first()
            if student:
                session.expunge(student)
            return student

    def get_by_primary_id(self, id: int) -> Optional[Student]:
        """Get student by primary key"""
        with db_manager.get_session() as session:
            student = session.query(Student).filter(Student.id == id).first()
            if student:
                session.expunge(student)
            return student

    def get_all(self) -> List[Student]:
        """Get all students"""
        with db_manager.get_session() as session:
            students = session.query(Student).all()
            for student in students:
                session.expunge(student)
            return students

    def get_by_class(self, class_name: str) -> List[Student]:
        """Get all students in a class"""
        with db_manager.get_session() as session:
            students = session.query(Student).filter(Student.class_name == class_name).all()
            for student in students:
                session.expunge(student)
            return students

    def update(self, student: Student) -> Student:
        """Update student information"""
        with db_manager.get_session() as session:
            existing = session.query(Student).filter(Student.student_id == student.student_id).first()
            if not existing:
                raise ValueError(f"Student {student.student_id} not found")

            existing.full_name = student.full_name
            existing.class_name = student.class_name
            existing.email = student.email
            existing.face_encoding_path = student.face_encoding_path
            existing.updated_at = datetime.now()

            session.flush()
            # Make the object accessible outside session
            session.expunge(existing)
            return existing

    def delete(self, student_id: str) -> bool:
        """Delete a student"""
        with db_manager.get_session() as session:
            student = session.query(Student).filter(Student.student_id == student_id).first()
            if student:
                session.delete(student)
                return True
            return False


class AttendanceRepository(IRepository):
    """Repository for Attendance records"""

    def create(self, attendance: AttendanceRecord) -> AttendanceRecord:
        """Create a new attendance record"""
        with db_manager.get_session() as session:
            session.add(attendance)
            session.flush()
            session.expunge(attendance)
            return attendance

    def get_by_id(self, record_id: int) -> Optional[AttendanceRecord]:
        """Get attendance record by ID"""
        with db_manager.get_session() as session:
            record = session.query(AttendanceRecord).filter(AttendanceRecord.id == record_id).first()
            if record:
                session.expunge(record)
            return record

    def get_all(self) -> List[AttendanceRecord]:
        """Get all attendance records"""
        with db_manager.get_session() as session:
            records = session.query(AttendanceRecord).all()
            for record in records:
                session.expunge(record)
            return records

    def get_by_student(self, student_id: str) -> List[AttendanceRecord]:
        """Get all attendance records for a student"""
        with db_manager.get_session() as session:
            records = session.query(AttendanceRecord).filter(
                AttendanceRecord.student_id == student_id
            ).order_by(AttendanceRecord.check_in_time.desc()).all()
            for record in records:
                session.expunge(record)
            return records

    def get_by_date(self, session_date: str) -> List[AttendanceRecord]:
        """Get all attendance records for a specific date"""
        with db_manager.get_session() as session:
            records = session.query(AttendanceRecord).filter(
                AttendanceRecord.session_date == session_date
            ).all()
            for record in records:
                session.expunge(record)
            return records

    def get_by_student_and_date(self, student_id: str, session_date: str) -> Optional[AttendanceRecord]:
        """Check if student already has attendance for a specific date"""
        with db_manager.get_session() as session:
            record = session.query(AttendanceRecord).filter(
                AttendanceRecord.student_id == student_id,
                AttendanceRecord.session_date == session_date
            ).first()
            if record:
                session.expunge(record)
            return record

    def update(self, attendance: AttendanceRecord) -> AttendanceRecord:
        """Update attendance record"""
        with db_manager.get_session() as session:
            existing = session.query(AttendanceRecord).filter(
                AttendanceRecord.id == attendance.id
            ).first()
            if not existing:
                raise ValueError(f"Attendance record {attendance.id} not found")

            existing.status = attendance.status
            existing.notes = attendance.notes

            session.flush()
            session.expunge(existing)
            return existing

    def delete(self, record_id: int) -> bool:
        """Delete an attendance record"""
        with db_manager.get_session() as session:
            record = session.query(AttendanceRecord).filter(AttendanceRecord.id == record_id).first()
            if record:
                session.delete(record)
                return True
            return False

