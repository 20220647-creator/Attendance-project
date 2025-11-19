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
    """Factory for creating face recognition strategies"""

    _strategies: Dict[str, Type[IFaceRecognitionStrategy]] = {
        'VGG-Face': VGGFaceStrategy,
        'Facenet': FacenetStrategy,
        'ArcFace': ArcFaceStrategy,
        'Facenet512': Facenet512Strategy
    }

    @classmethod
    def create_strategy(cls, model_name: str) -> IFaceRecognitionStrategy:
        """
        Create a face recognition strategy based on model name

        Args:
            model_name: Name of the model ('VGG-Face', 'Facenet', 'ArcFace', 'Facenet512')

        Returns:
            Instance of the requested strategy

        Raises:
            ValueError: If model name is not supported
        """
        strategy_class = cls._strategies.get(model_name)

        if strategy_class is None:
            available_models = ', '.join(cls._strategies.keys())
            raise ValueError(
                f"Model '{model_name}' is not supported. "
                f"Available models: {available_models}"
            )

        return strategy_class()

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

