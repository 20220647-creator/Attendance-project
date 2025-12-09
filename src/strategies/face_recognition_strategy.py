"""
Strategy là mẫu thiết kế cho phép chọn thuật toán tại thời điểm chạy.
Trong trường hợp này, chúng ta có thể chọn các chiến lược nhận diện khuôn mặt khác nhau như VGG-Face, Facenet, ArcFace, v.v.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import os
import numpy as np
from deepface import DeepFace
import cv2

from src.models.models import FaceRecognitionResult
from src.config.config import config

"""Lớp này là lớp cha cho tất cả các chiến lược nhận diện khuôn mặt."""
class IFaceRecognitionStrategy(ABC):
    """Interface for Face Recognition Strategy"""

    # Mọi phương thức trong lớp này phải được các lớp con triển khai.
    # @abstractmethod sẽ buộc các lớp con phải triển khai các phương thức này.
    @abstractmethod
    def recognize_face(self, image_path: str, database_path: str) -> List[Dict[str, Any]]:
        """Recognize face in image against database"""
        pass

    @abstractmethod
    def verify_face(self, img1_path: str, img2_path: str) -> Dict[str, Any]:
        """Verify if two faces are the same person"""
        pass

    @abstractmethod
    def extract_embedding(self, image_path: str) -> np.ndarray:
        """Extract face embedding from image"""
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """Get the model name"""
        pass


class VGGFaceStrategy(IFaceRecognitionStrategy):
    """Lớp con triển khai chiến lược nhận diện khuôn mặt VGG-Face, sẽ kế thừa từ IFaceRecognitionStrategy."""

    #Khởi tạo các thuộc tính cụ thể cho chiến lược VGG-Face.
    def __init__(self):
        self.model_name = "VGG-Face"
        self.distance_metric = config.DISTANCE_METRIC # Khoảng cách để so sánh khuôn mặt lấy từ config
        self.detection_backend = config.DETECTION_BACKEND # Phương pháp phát hiện khuôn mặt lấy từ config

    #Phương thức nhận diện khuôn mặt sử dụng mô hình VGG-Face, tham số là đường dẫn hình ảnh và cơ sở dữ liệu.
    # Trả về danh sách kết quả nhận diện dưới dạng Dict hoặc mảng numpy.
    def recognize_face(self, image_path: str, database_path: str) -> List[Dict[str, Any]]:
        try:
            # DeepFace.find trả về danh sách các DataFrame
            result = DeepFace.find(
                img_path=image_path,
                db_path=database_path,
                model_name=self.model_name, # Sử dụng mô hình VGG-Face
                distance_metric=self.distance_metric, # Sử dụng khoảng cách từ config
                detector_backend=self.detection_backend, # Sử dụng backend phát hiện khuôn mặt từ config
                enforce_detection=False,  # Cho phép xử lý hình ảnh chất lượng kém
                silent=True
            )

            # Nếu có kết quả, kiểm tra DataFrame đầu tiên
            if result and len(result) > 0:
                df = result[0]
                # Kiểm tra nếu DataFrame có độ dài > 0 (có khuôn mặt được nhận diện)
                if hasattr(df, '__len__') and len(df) > 0:
                    return result # Trả về kết quả tìm kiếm

            # Nếu không có kết quả hợp lệ, trả về danh sách rỗng
            return []

        except ValueError as e:
            error_msg = str(e)
            if "Face could not be detected" in error_msg:
                print(f"⚠ No face detected in image with model {self.model_name}")
            else:
                print(f"✗ Error: {error_msg}")
            return []

        except Exception as e:
            error_msg = str(e)
            if "Length of values" in error_msg or "does not match" in error_msg:
                return []
            else:
                print(f"✗ Error in VGG-Face recognition: {error_msg}")
            return []

    def verify_face(self, img1_path: str, img2_path: str) -> Dict[str, Any]:
        """Hàm xác minh khuôn mặt sử dụng mô hình VGG-Face, trả về kết quả dưới dạng Dict."""
        try:
            result = DeepFace.verify(
                img1_path=img1_path,
                img2_path=img2_path,
                model_name=self.model_name, # Sử dụng mô hình VGG-Face
                distance_metric=self.distance_metric, # Sử dụng khoảng cách từ config
                detector_backend=self.detection_backend, # Sử dụng backend phát hiện khuôn mặt từ config
                enforce_detection=True # Bắt buộc phát hiện khuôn mặt trong cả hai hình ảnh
            )
            return result # Trả về kết quả xác minh
        except Exception as e:
            print(f"Error in VGG-Face verification: {str(e)}")
            return {"verified": False, "distance": 1.0} # Trả về kết quả mặc định nếu có lỗi, "verified" là False và khoảng cách là 1.0

    def extract_embedding(self, image_path: str) -> np.ndarray:
        """Trích xuất embedding khuôn mặt sử dụng mô hình VGG-Face, trả về embedding dưới dạng mảng numpy."""
        try:
            #represent trả về danh sách các embedding
            embedding = DeepFace.represent(
                img_path=image_path,
                model_name=self.model_name,
                detector_backend=self.detection_backend,
                enforce_detection=True
            )
            return np.array(embedding[0]["embedding"])
        except Exception as e:
            print(f"Error extracting VGG-Face embedding: {str(e)}")
            return np.array([])

    def get_model_name(self) -> str:
        return self.model_name


class FacenetStrategy(IFaceRecognitionStrategy):

    def __init__(self):
        self.model_name = "Facenet"
        self.distance_metric = config.DISTANCE_METRIC
        self.detection_backend = config.DETECTION_BACKEND

    def recognize_face(self, image_path: str, database_path: str) -> List[Dict[str, Any]]:
        try:
            # Use enforce_detection=False to handle poor quality images
            result = DeepFace.find(
                img_path=image_path,
                db_path=database_path,
                model_name=self.model_name,
                distance_metric=self.distance_metric,
                detector_backend=self.detection_backend,
                enforce_detection=False,
                silent=True
            )

            # Validate result
            if result and len(result) > 0:
                df = result[0]
                if hasattr(df, '__len__') and len(df) > 0:
                    return result
            return []

        except ValueError as e:
            error_msg = str(e)
            if "Face could not be detected" in error_msg:
                print(f"⚠ No face detected with Facenet")
            else:
                print(f"✗ Error: {error_msg}")
            return []

        except Exception as e:
            error_msg = str(e)
            # Pandas error when no matches - this is normal
            if "Length of values" in error_msg or "does not match" in error_msg:
                return []
            else:
                print(f"✗ Error in Facenet recognition: {error_msg}")
            return []

    def verify_face(self, img1_path: str, img2_path: str) -> Dict[str, Any]:
        try:
            result = DeepFace.verify(
                img1_path=img1_path,
                img2_path=img2_path,
                model_name=self.model_name,
                distance_metric=self.distance_metric,
                detector_backend=self.detection_backend,
                enforce_detection=True
            )
            return result
        except Exception as e:
            print(f"Error in Facenet verification: {str(e)}")
            return {"verified": False, "distance": 1.0}

    def extract_embedding(self, image_path: str) -> np.ndarray:
        try:
            embedding = DeepFace.represent(
                img_path=image_path,
                model_name=self.model_name,
                detector_backend=self.detection_backend,
                enforce_detection=True
            )
            return np.array(embedding[0]["embedding"])
        except Exception as e:
            print(f"Error extracting Facenet embedding: {str(e)}")
            return np.array([])

    def get_model_name(self) -> str:
        return self.model_name


class ArcFaceStrategy(IFaceRecognitionStrategy):

    def __init__(self):
        self.model_name = "ArcFace"
        self.distance_metric = config.DISTANCE_METRIC
        self.detection_backend = config.DETECTION_BACKEND

    def recognize_face(self, image_path: str, database_path: str) -> List[Dict[str, Any]]:
        try:
            result = DeepFace.find(
                img_path=image_path,
                db_path=database_path,
                model_name=self.model_name,
                distance_metric=self.distance_metric,
                detector_backend=self.detection_backend,
                enforce_detection=False,
                silent=True
            )

            # Validate result
            if result and len(result) > 0:
                df = result[0]
                if hasattr(df, '__len__') and len(df) > 0:
                    return result
            return []

        except ValueError as e:
            error_msg = str(e)
            if "Face could not be detected" in error_msg:
                print(f"⚠ No face detected with ArcFace")
            else:
                print(f"✗ Error: {error_msg}")
            return []

        except Exception as e:
            error_msg = str(e)
            # Pandas error when no matches - this is normal
            if "Length of values" in error_msg or "does not match" in error_msg:
                return []
            else:
                print(f"✗ Error in ArcFace recognition: {error_msg}")
            return []

    def verify_face(self, img1_path: str, img2_path: str) -> Dict[str, Any]:
        try:
            result = DeepFace.verify(
                img1_path=img1_path,
                img2_path=img2_path,
                model_name=self.model_name,
                distance_metric=self.distance_metric,
                detector_backend=self.detection_backend,
                enforce_detection=True
            )
            return result
        except Exception as e:
            print(f"Error in ArcFace verification: {str(e)}")
            return {"verified": False, "distance": 1.0}

    def extract_embedding(self, image_path: str) -> np.ndarray:
        try:
            embedding = DeepFace.represent(
                img_path=image_path,
                model_name=self.model_name,
                detector_backend=self.detection_backend,
                enforce_detection=True
            )
            return np.array(embedding[0]["embedding"])
        except Exception as e:
            print(f"Error extracting ArcFace embedding: {str(e)}")
            return np.array([])

    def get_model_name(self) -> str:
        return self.model_name


class Facenet512Strategy(IFaceRecognitionStrategy):

    def __init__(self):
        self.model_name = "Facenet512"
        self.distance_metric = config.DISTANCE_METRIC
        self.detection_backend = config.DETECTION_BACKEND

    def recognize_face(self, image_path: str, database_path: str) -> List[Dict[str, Any]]:
        try:
            # Use enforce_detection=False to handle poor quality images
            result = DeepFace.find(
                img_path=image_path,
                db_path=database_path,
                model_name=self.model_name,
                distance_metric=self.distance_metric,
                detector_backend=self.detection_backend,
                enforce_detection=False,
                silent=True
            )

            if result and len(result) > 0:
                df = result[0]
                if hasattr(df, '__len__') and len(df) > 0:
                    return result
            return []

        except ValueError as e:
            error_msg = str(e)
            if "Face could not be detected" in error_msg:
                print(f"⚠ No face detected with Facenet512")
            else:
                print(f"✗ Error: {error_msg}")
            return []

        except Exception as e:
            error_msg = str(e)
            if "Length of values" in error_msg or "does not match" in error_msg:
                return []
            else:
                print(f"✗ Error in Facenet512 recognition: {error_msg}")
            return []

    def verify_face(self, img1_path: str, img2_path: str) -> Dict[str, Any]:
        try:
            result = DeepFace.verify(
                img1_path=img1_path,
                img2_path=img2_path,
                model_name=self.model_name,
                distance_metric=self.distance_metric,
                detector_backend=self.detection_backend,
                enforce_detection=True
            )
            return result
        except Exception as e:
            print(f"Error in Facenet512 verification: {str(e)}")
            return {"verified": False, "distance": 1.0}

    def extract_embedding(self, image_path: str) -> np.ndarray:
        try:
            embedding = DeepFace.represent(
                img_path=image_path,
                model_name=self.model_name,
                detector_backend=self.detection_backend,
                enforce_detection=True
            )
            return np.array(embedding[0]["embedding"])
        except Exception as e:
            print(f"Error extracting Facenet512 embedding: {str(e)}")
            return np.array([])

    def get_model_name(self) -> str:
        return self.model_name


class FaceRecognitionContext:
    """Lớp ngữ cảnh để sử dụng các chiến lược nhận diện khuôn mặt khác nhau."""

    # Khởi tạo với một chiến lược cụ thể, với strategy là một thể hiện của IFaceRecognitionStrategy.
    def __init__(self, strategy: IFaceRecognitionStrategy):
        self._strategy = strategy

    #property để lấy và đặt chiến lược hiện tại.
    @property
    def strategy(self) -> IFaceRecognitionStrategy:
        return self._strategy
    #setter để thay đổi chiến lược hiện tại.
    @strategy.setter
    def strategy(self, strategy: IFaceRecognitionStrategy):
        self._strategy = strategy
    # Phương thức để nhận diện khuôn mặt, ủy quyền cho chiến lược hiện tại.
    def recognize_face(self, image_path: str, database_path: str) -> List[Dict[str, Any]]:
        """Delegate recognition to strategy"""
        return self._strategy.recognize_face(image_path, database_path)

    # Phương thức để xác minh khuôn mặt, ủy quyền cho chiến lược hiện tại.
    def verify_face(self, img1_path: str, img2_path: str) -> Dict[str, Any]:
        """Delegate verification to strategy"""
        return self._strategy.verify_face(img1_path, img2_path)

    # Phương thức để trích xuất embedding khuôn mặt, ủy quyền cho chiến lược hiện tại.
    def extract_embedding(self, image_path: str) -> np.ndarray:
        """Delegate embedding extraction to strategy"""
        return self._strategy.extract_embedding(image_path)

    # Phương thức để lấy tên mô hình hiện tại, ủy quyền cho chiến lược hiện tại.
    def get_model_name(self) -> str:
        """Get current model name"""
        return self._strategy.get_model_name()