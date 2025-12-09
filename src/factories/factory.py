"""
Factory Pattern for creating Face Recognition Strategies
"""
from typing import Dict, Type
from src.strategies.face_recognition_strategy import (
    IFaceRecognitionStrategy,
    VGGFaceStrategy,
    FacenetStrategy,
    ArcFaceStrategy,
    Facenet512Strategy
)


class FaceRecognitionStrategyFactory:
    """Lớp factory để tạo các chiến lược nhận diện khuôn mặt khác nhau"""

    _strategies: Dict[str, Type[IFaceRecognitionStrategy]] = {
        'VGG-Face': VGGFaceStrategy,
        'Facenet': FacenetStrategy,
        'ArcFace': ArcFaceStrategy,
        'Facenet512': Facenet512Strategy
    }

    # @class method để tạo chiến lược dựa trên tên mô hình
    @classmethod
    def create_strategy(cls, model_name: str) -> IFaceRecognitionStrategy:
        """
        Định nghĩa phương thức tạo nhận diện khuôn mặt dựa trên tên mô hình
        """

        # Tìm lớp chiến lược tương ứng với tên mô hình
        # cls là tham chiếu đến lớp hiện tại
        strategy_class = cls._strategies.get(model_name)

        # Nếu không tìm thấy, ném lỗi
        if strategy_class is None:
            available_models = ', '.join(cls._strategies.keys())
            raise ValueError(
                f"Model '{model_name}' is not supported. "
                f"Available models: {available_models}"
            )

        return strategy_class()

    # @class method để lấy danh sách các mô hình có sẵn
    @classmethod
    def get_available_models(cls) -> list:
        """Get list of available model names"""
        return list(cls._strategies.keys())

    @classmethod
    def register_strategy(cls, model_name: str, strategy_class: Type[IFaceRecognitionStrategy]):
        """
        Register a new strategy (for extensibility)

        Args:
            model_name: Name of the model
            strategy_class: Strategy class to register
        """
        cls._strategies[model_name] = strategy_class

