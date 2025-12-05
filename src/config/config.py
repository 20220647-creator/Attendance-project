"""
Configuration module for Face Recognition Attendance System
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application Configuration using Singleton Pattern"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # Database
        self.DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///attendance.db')

        # Model Configuration
        self.DEFAULT_MODEL = os.getenv('DEFAULT_MODEL', 'VGG-Face')
        self.AVAILABLE_MODELS = ['VGG-Face', 'Facenet', 'ArcFace', 'Facenet512']
        self.DETECTION_BACKEND = os.getenv('DETECTION_BACKEND', 'opencv')
        self.DISTANCE_METRIC = os.getenv('DISTANCE_METRIC', 'cosine')

        # Paths
        self.STUDENT_DATABASE_PATH = os.getenv('STUDENT_DATABASE_PATH', 'data/students')
        self.ATTENDANCE_LOG_PATH = os.getenv('ATTENDANCE_LOG_PATH', 'data/attendance_logs')
        self.MODELS_PATH = 'models'

        # Face Recognition Settings
        # STRICTER thresholds to prevent false positives (wrong person matches)
        self.RECOGNITION_THRESHOLD = {
            'VGG-Face': 0.50,     # Stricter: was 0.68 - prevents matching wrong faces
            'Facenet': 0.45,      # Stricter: was 0.60 - better accuracy
            'Facenet512': 0.40,   # Stricter: was 0.50 - most accurate
            'ArcFace': 0.68       # Stricter: was 0.85 - prevents false matches
        }

        # Minimum confidence required for attendance (0.6 = 60%)
        self.MIN_CONFIDENCE_FOR_ATTENDANCE = 0.60

        # Multiple samples for better recognition
        self.NUM_FACE_SAMPLES = 10  # Number of sample images to capture per student
        self.SAMPLE_CAPTURE_DELAY = 0.5  # Delay between captures (seconds)

        # Ensure directories exist
        self._create_directories()

        self._initialized = True

    def _create_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [
            self.STUDENT_DATABASE_PATH,
            self.ATTENDANCE_LOG_PATH,
            self.MODELS_PATH,
            'data/models'  # For Haar Cascade
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

        # Initialize Haar Cascade to avoid Unicode path issues
        self._init_haar_cascade()

    def _init_haar_cascade(self):
        """Copy Haar Cascade to local directory to avoid Unicode path issues"""
        try:
            import cv2
            import shutil

            cascade_dest = os.path.join('data', 'models', 'haarcascade_frontalface_default.xml')

            # Skip if already exists
            if os.path.exists(cascade_dest):
                return

            # Copy from OpenCV installation
            cascade_src = os.path.join(cv2.data.haarcascades, 'haarcascade_frontalface_default.xml')

            if os.path.exists(cascade_src):
                shutil.copy(cascade_src, cascade_dest)
        except Exception as e:
            # Silent fail - will use OpenCV default path as fallback
            pass

    def get_threshold(self, model_name: str) -> float:
        """Get recognition threshold for specific model"""
        return self.RECOGNITION_THRESHOLD.get(model_name, 0.4)


# Global config instance
config = Config()

