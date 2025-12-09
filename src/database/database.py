"""
Database manager using Singleton Pattern
Quản lý cơ sở dữ liệu sử dụng mẫu thiết kế Singleton
"""
# Import thư viện SQLAlchemy để làm việc với cơ sở dữ liệu
from sqlalchemy import create_engine  # Tạo kết nối đến database
from sqlalchemy.orm import sessionmaker, Session  # Tạo session để thực hiện các thao tác CRUD
from sqlalchemy.pool import StaticPool  # Pool kết nối cho SQLite
from contextlib import contextmanager  # Decorator để tạo context manager
from typing import Generator  # Type hint cho generator

from src.models.models import Base  # Base class cho các model SQLAlchemy
from src.config.config import config  # Cấu hình ứng dụng


class DatabaseManager:
    """
    Singleton Database Manager
    Lớp quản lý cơ sở dữ liệu theo mẫu Singleton
    - Đảm bảo chỉ có một instance duy nhất trong toàn bộ ứng dụng
    - Quản lý kết nối và session database
    """
    _instance = None  # Biến lưu trữ instance duy nhất
    _engine = None  # Engine kết nối database
    _session_factory = None  # Factory để tạo session

    def __new__(cls):
        """
        Override __new__ để triển khai Singleton Pattern
        Chỉ tạo instance mới nếu chưa tồn tại
        """
        if cls._instance is None:
            # Tạo instance mới nếu chưa có
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialized = False  # Đánh dấu chưa khởi tạo
        return cls._instance  # Trả về instance duy nhất

    def __init__(self):
        """
        Khởi tạo database manager
        Chỉ thực hiện khởi tạo một lần duy nhất
        """
        if self._initialized:
            return  # Nếu đã khởi tạo rồi thì bỏ qua

        self._initialize_database()  # Thực hiện khởi tạo database
        self._initialized = True  # Đánh dấu đã khởi tạo

    def _initialize_database(self):
        """
        Initialize database connection and create tables
        Khởi tạo kết nối database và tạo các bảng
        """
        # Kiểm tra nếu sử dụng SQLite, dùng StaticPool để tránh lỗi đa luồng
        if config.DATABASE_URL.startswith('sqlite'):
            self._engine = create_engine(
                config.DATABASE_URL,  # URL kết nối database
                connect_args={'check_same_thread': False},  # Cho phép truy cập từ nhiều thread
                poolclass=StaticPool  # Sử dụng pool tĩnh cho SQLite
            )
        else:
            # Với các database khác (PostgreSQL, MySQL), tạo engine thông thường
            self._engine = create_engine(config.DATABASE_URL)

        # Tạo session factory - dùng để tạo các session làm việc với database
        self._session_factory = sessionmaker(bind=self._engine)

        # Tạo tất cả các bảng đã định nghĩa trong models
        Base.metadata.create_all(self._engine)

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Context manager for database sessions
        Context manager để quản lý session database

        Cách sử dụng:
            with db_manager.get_session() as session:
                # thực hiện các thao tác với session
                session.query(Student).all()

        Tự động:
        - Commit nếu không có lỗi
        - Rollback nếu có exception
        - Đóng session khi kết thúc
        """
        session = self._session_factory()  # Tạo session mới
        try:
            yield session  # Trả session cho code sử dụng
            session.commit()  # Commit các thay đổi nếu thành công
        except Exception as e:
            session.rollback()  # Rollback nếu có lỗi
            raise e  # Ném lại exception
        finally:
            session.close()  # Luôn đóng session khi kết thúc

    def create_tables(self):
        """
        Create all tables in the database
        Tạo tất cả các bảng trong database
        """
        Base.metadata.create_all(self._engine)

    def drop_tables(self):
        """
        Drop all tables from the database
        Xóa tất cả các bảng trong database
        """
        Base.metadata.drop_all(self._engine)


# Global database manager instance
# Tạo instance toàn cục để sử dụng trong toàn bộ ứng dụng
db_manager = DatabaseManager()
