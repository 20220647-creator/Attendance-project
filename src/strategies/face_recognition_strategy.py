"""
Strategy Pattern for Face Recognition Algorithms
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import os
import numpy as np
from deepface import DeepFace
import cv2

from src.models.models import FaceRecognitionResult
from src.config.config import config


class IFaceRecognitionStrategy(ABC):
    """Interface for Face Recognition Strategy"""

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
    """VGG-Face recognition strategy"""

    def __init__(self):
        self.model_name = "VGG-Face"
        self.distance_metric = config.DISTANCE_METRIC
        self.detection_backend = config.DETECTION_BACKEND

    def recognize_face(self, image_path: str, database_path: str) -> List[Dict[str, Any]]:
        """Recognize face using VGG-Face model"""
        try:
            result = DeepFace.find(
                img_path=image_path,
                db_path=database_path,
                model_name=self.model_name,
                distance_metric=self.distance_metric,
                detector_backend=self.detection_backend,
                enforce_detection=True,
                silent=True
            )
            return result
        except Exception as e:
            print(f"Error in VGG-Face recognition: {str(e)}")
            return []

    def verify_face(self, img1_path: str, img2_path: str) -> Dict[str, Any]:
        """Verify face using VGG-Face model"""
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
            print(f"Error in VGG-Face verification: {str(e)}")
            return {"verified": False, "distance": 1.0}

    def extract_embedding(self, image_path: str) -> np.ndarray:
        """Extract embedding using VGG-Face model"""
        try:
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
    """Facenet recognition strategy"""

    def __init__(self):
        self.model_name = "Facenet"
        self.distance_metric = config.DISTANCE_METRIC
        self.detection_backend = config.DETECTION_BACKEND

    def recognize_face(self, image_path: str, database_path: str) -> List[Dict[str, Any]]:
        """Recognize face using Facenet model"""
        try:
            result = DeepFace.find(
                img_path=image_path,
                db_path=database_path,
                model_name=self.model_name,
                distance_metric=self.distance_metric,
                detector_backend=self.detection_backend,
                enforce_detection=True,
                silent=True
            )
            return result
        except Exception as e:
            print(f"Error in Facenet recognition: {str(e)}")
            return []

    def verify_face(self, img1_path: str, img2_path: str) -> Dict[str, Any]:
        """Verify face using Facenet model"""
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
        """Extract embedding using Facenet model"""
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
    """ArcFace recognition strategy"""

    def __init__(self):
        self.model_name = "ArcFace"
        self.distance_metric = config.DISTANCE_METRIC
        self.detection_backend = config.DETECTION_BACKEND

    def recognize_face(self, image_path: str, database_path: str) -> List[Dict[str, Any]]:
        """Recognize face using ArcFace model"""
        try:
            result = DeepFace.find(
                img_path=image_path,
                db_path=database_path,
                model_name=self.model_name,
                distance_metric=self.distance_metric,
                detector_backend=self.detection_backend,
                enforce_detection=True,
                silent=True
            )
            return result
        except Exception as e:
            print(f"Error in ArcFace recognition: {str(e)}")
            return []

    def verify_face(self, img1_path: str, img2_path: str) -> Dict[str, Any]:
        """Verify face using ArcFace model"""
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
        """Extract embedding using ArcFace model"""
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
    """Facenet512 recognition strategy"""

    def __init__(self):
        self.model_name = "Facenet512"
        self.distance_metric = config.DISTANCE_METRIC
        self.detection_backend = config.DETECTION_BACKEND

    def recognize_face(self, image_path: str, database_path: str) -> List[Dict[str, Any]]:
        """Recognize face using Facenet512 model"""
        try:
            result = DeepFace.find(
                img_path=image_path,
                db_path=database_path,
                model_name=self.model_name,
                distance_metric=self.distance_metric,
                detector_backend=self.detection_backend,
                enforce_detection=True,
                silent=True
            )
            return result
        except Exception as e:
            print(f"Error in Facenet512 recognition: {str(e)}")
            return []

    def verify_face(self, img1_path: str, img2_path: str) -> Dict[str, Any]:
        """Verify face using Facenet512 model"""
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
        """Extract embedding using Facenet512 model"""
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
    """Context class for Face Recognition Strategy Pattern"""

    def __init__(self, strategy: IFaceRecognitionStrategy):
        self._strategy = strategy

    @property
    def strategy(self) -> IFaceRecognitionStrategy:
        return self._strategy

    @strategy.setter
    def strategy(self, strategy: IFaceRecognitionStrategy):
        self._strategy = strategy

    def recognize_face(self, image_path: str, database_path: str) -> List[Dict[str, Any]]:
        """Delegate recognition to strategy"""
        return self._strategy.recognize_face(image_path, database_path)

    def verify_face(self, img1_path: str, img2_path: str) -> Dict[str, Any]:
        """Delegate verification to strategy"""
        return self._strategy.verify_face(img1_path, img2_path)

    def extract_embedding(self, image_path: str) -> np.ndarray:
        """Delegate embedding extraction to strategy"""
        return self._strategy.extract_embedding(image_path)

    def get_model_name(self) -> str:
        """Get current model name"""
        return self._strategy.get_model_name()

