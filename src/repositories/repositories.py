"""
Repository pattern for data access layer
Mẫu Repository cho tầng truy cập dữ liệu
- Tách biệt logic truy cập dữ liệu khỏi logic nghiệp vụ
- Cung cấp interface thống nhất cho các thao tác CRUD
"""
# Import các thư viện cần thiết
from abc import ABC, abstractmethod  # Abstract Base Class để định nghĩa interface
from typing import List, Optional  # Type hints
from datetime import datetime, date  # Xử lý ngày giờ
from sqlalchemy.exc import IntegrityError  # Exception khi vi phạm ràng buộc database

from src.models.models import Student, AttendanceRecord  # Import các model
from src.database.database import db_manager  # Database manager singleton


class IRepository(ABC):
    """
    Interface for Repository Pattern
    Giao diện cho mẫu Repository
    - Định nghĩa các phương thức trừu tượng mà tất cả Repository phải implement
    - Tuân thủ nguyên tắc Dependency Inversion (SOLID)
    """

    @abstractmethod
    def create(self, entity):
        """Tạo mới một entity"""
        pass

    @abstractmethod
    def get_by_id(self, entity_id):
        """Lấy entity theo ID"""
        pass

    @abstractmethod
    def get_all(self):
        """Lấy tất cả entity"""
        pass

    @abstractmethod
    def update(self, entity):
        """Cập nhật entity"""
        pass

    @abstractmethod
    def delete(self, entity_id):
        """Xóa entity theo ID"""
        pass


class StudentRepository(IRepository):
    """
    Repository for Student entity
    Repository quản lý sinh viên
    - Implement các phương thức CRUD cho Student
    - Xử lý truy vấn database thông qua SQLAlchemy
    """

    def create(self, student: Student) -> Student:
        """
        Create a new student
        Tạo sinh viên mới trong database

        Args:
            student: Đối tượng Student cần tạo

        Returns:
            Student đã được tạo với ID

        Raises:
            ValueError: Nếu student_id đã tồn tại
        """
        with db_manager.get_session() as session:
            try:
                session.add(student)  # Thêm student vào session
                session.flush()  # Flush để lấy ID được generate
                # Tách object khỏi session để có thể sử dụng bên ngoài
                session.expunge(student)
                return student
            except IntegrityError:
                # Lỗi khi student_id đã tồn tại (vi phạm unique constraint)
                raise ValueError(f"Student with ID {student.student_id} already exists")

    def get_by_id(self, student_id: str) -> Optional[Student]:
        """
        Get student by student_id
        Lấy sinh viên theo mã sinh viên

        Args:
            student_id: Mã sinh viên cần tìm

        Returns:
            Student nếu tìm thấy, None nếu không
        """
        with db_manager.get_session() as session:
            # Truy vấn student theo student_id
            student = session.query(Student).filter(Student.student_id == student_id).first()
            if student:
                session.expunge(student)  # Tách khỏi session
            return student

    def get_by_primary_id(self, id: int) -> Optional[Student]:
        """
        Get student by primary key
        Lấy sinh viên theo khóa chính (id tự động tăng)
        """
        with db_manager.get_session() as session:
            student = session.query(Student).filter(Student.id == id).first()
            if student:
                session.expunge(student)
            return student

    def get_all(self) -> List[Student]:
        """
        Get all students
        Lấy tất cả sinh viên trong database

        Returns:
            Danh sách tất cả Student
        """
        with db_manager.get_session() as session:
            students = session.query(Student).all()  # Lấy tất cả
            for student in students:
                session.expunge(student)  # Tách từng student khỏi session
            return students

    def get_by_class(self, class_name: str) -> List[Student]:
        """
        Get all students in a class
        Lấy tất cả sinh viên trong một lớp

        Args:
            class_name: Tên lớp cần tìm

        Returns:
            Danh sách sinh viên trong lớp
        """
        with db_manager.get_session() as session:
            students = session.query(Student).filter(Student.class_name == class_name).all()
            for student in students:
                session.expunge(student)
            return students

    def update(self, student: Student) -> Student:
        """
        Update student information
        Cập nhật thông tin sinh viên

        Args:
            student: Đối tượng Student với thông tin mới

        Returns:
            Student đã được cập nhật

        Raises:
            ValueError: Nếu không tìm thấy sinh viên
        """
        with db_manager.get_session() as session:
            # Tìm student hiện tại trong database
            existing = session.query(Student).filter(Student.student_id == student.student_id).first()
            if not existing:
                raise ValueError(f"Student {student.student_id} not found")

            # Cập nhật các trường
            existing.full_name = student.full_name
            existing.class_name = student.class_name
            existing.email = student.email
            existing.face_encoding_path = student.face_encoding_path
            existing.updated_at = datetime.now()  # Cập nhật thời gian

            session.flush()  # Lưu thay đổi
            session.expunge(existing)  # Tách khỏi session
            return existing

    def delete(self, student_id: str) -> bool:
        """
        Delete a student
        Xóa sinh viên khỏi database

        Args:
            student_id: Mã sinh viên cần xóa

        Returns:
            True nếu xóa thành công, False nếu không tìm thấy
        """
        with db_manager.get_session() as session:
            student = session.query(Student).filter(Student.student_id == student_id).first()
            if student:
                session.delete(student)  # Xóa student (cascade sẽ xóa attendance records)
                return True
            return False


class AttendanceRepository(IRepository):
    """
    Repository for Attendance records
    Repository quản lý bản ghi điểm danh
    - Implement các phương thức CRUD cho AttendanceRecord
    - Hỗ trợ các truy vấn theo sinh viên, ngày, hoặc kết hợp
    """

    def create(self, attendance: AttendanceRecord) -> AttendanceRecord:
        """
        Create a new attendance record
        Tạo bản ghi điểm danh mới

        Args:
            attendance: Đối tượng AttendanceRecord cần tạo

        Returns:
            AttendanceRecord đã được tạo
        """
        with db_manager.get_session() as session:
            session.add(attendance)
            session.flush()
            session.expunge(attendance)
            return attendance

    def get_by_id(self, record_id: int) -> Optional[AttendanceRecord]:
        """
        Get attendance record by ID
        Lấy bản ghi điểm danh theo ID
        """
        with db_manager.get_session() as session:
            record = session.query(AttendanceRecord).filter(AttendanceRecord.id == record_id).first()
            if record:
                session.expunge(record)
            return record

    def get_all(self) -> List[AttendanceRecord]:
        """
        Get all attendance records
        Lấy tất cả bản ghi điểm danh
        """
        with db_manager.get_session() as session:
            records = session.query(AttendanceRecord).all()
            for record in records:
                session.expunge(record)
            return records

    def get_by_student(self, student_id: str) -> List[AttendanceRecord]:
        """
        Get all attendance records for a student
        Lấy tất cả bản ghi điểm danh của một sinh viên

        Args:
            student_id: Mã sinh viên

        Returns:
            Danh sách bản ghi, sắp xếp theo thời gian giảm dần
        """
        with db_manager.get_session() as session:
            records = session.query(AttendanceRecord).filter(
                AttendanceRecord.student_id == student_id
            ).order_by(AttendanceRecord.check_in_time.desc()).all()  # Sắp xếp theo thời gian mới nhất
            for record in records:
                session.expunge(record)
            return records

    def get_by_date(self, session_date: str) -> List[AttendanceRecord]:
        """
        Get all attendance records for a specific date
        Lấy tất cả bản ghi điểm danh của một ngày cụ thể

        Args:
            session_date: Ngày cần truy vấn (định dạng YYYY-MM-DD)

        Returns:
            Danh sách bản ghi điểm danh trong ngày
        """
        with db_manager.get_session() as session:
            records = session.query(AttendanceRecord).filter(
                AttendanceRecord.session_date == session_date
            ).all()
            for record in records:
                session.expunge(record)
            return records

    def get_by_student_and_date(self, student_id: str, session_date: str) -> Optional[AttendanceRecord]:
        """
        Check if student already has attendance for a specific date
        Kiểm tra sinh viên đã điểm danh trong ngày chưa

        Args:
            student_id: Mã sinh viên
            session_date: Ngày cần kiểm tra

        Returns:
            AttendanceRecord nếu đã điểm danh, None nếu chưa
        """
        with db_manager.get_session() as session:
            record = session.query(AttendanceRecord).filter(
                AttendanceRecord.student_id == student_id,  # Điều kiện 1: đúng sinh viên
                AttendanceRecord.session_date == session_date  # Điều kiện 2: đúng ngày
            ).first()
            if record:
                session.expunge(record)
            return record

    def update(self, attendance: AttendanceRecord) -> AttendanceRecord:
        """
        Update attendance record
        Cập nhật bản ghi điểm danh

        Args:
            attendance: Đối tượng AttendanceRecord với thông tin mới

        Returns:
            AttendanceRecord đã được cập nhật

        Raises:
            ValueError: Nếu không tìm thấy bản ghi
        """
        with db_manager.get_session() as session:
            existing = session.query(AttendanceRecord).filter(
                AttendanceRecord.id == attendance.id
            ).first()
            if not existing:
                raise ValueError(f"Attendance record {attendance.id} not found")

            # Cập nhật các trường
            existing.status = attendance.status
            existing.notes = attendance.notes

            session.flush()
            session.expunge(existing)
            return existing

    def delete(self, record_id: int) -> bool:
        """
        Delete an attendance record
        Xóa bản ghi điểm danh

        Args:
            record_id: ID của bản ghi cần xóa

        Returns:
            True nếu xóa thành công, False nếu không tìm thấy
        """
        with db_manager.get_session() as session:
            record = session.query(AttendanceRecord).filter(AttendanceRecord.id == record_id).first()
            if record:
                session.delete(record)
                return True
            return False
