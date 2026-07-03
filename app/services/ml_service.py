"""
ML model service with caching and optimization.
"""
import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Optional

import joblib
import numpy as np

from app.core.config import settings
from app.core.exceptions import MLModelError

logger = logging.getLogger(__name__)


class MLService:
    """Service for ML model operations with caching."""

    _model_cache: dict = {}
    _metadata_cache: Optional[dict] = None

    @staticmethod
    def load_model(model_name: str):
        """Load ML model from disk with caching.

        Args:
            model_name: Name of model ("base" or "equipe")

        Returns:
            Loaded ML model pipeline

        Raises:
            MLModelError: If model file not found or loading fails
        """
        if model_name in MLService._model_cache:
            logger.debug(f"Loading {model_name} model from cache")
            return MLService._model_cache[model_name]

        model_path = (
            settings.MODEL_BASE_PATH
            if model_name == "base"
            else settings.MODEL_EQUIPE_PATH
        )

        path = Path(model_path)
        if not path.exists():
            msg = f"Model file not found: {model_path}"
            logger.error(msg)
            raise MLModelError(msg)

        try:
            logger.info(f"Loading {model_name} model from {model_path}")
            model = joblib.load(model_path)
            MLService._model_cache[model_name] = model
            logger.info(f"Successfully loaded {model_name} model")
            return model
        except Exception as e:
            msg = f"Failed to load {model_name} model: {str(e)}"
            logger.error(msg)
            raise MLModelError(msg)

    @staticmethod
    def load_metadata() -> dict:
        """Load model metadata from JSON file with caching.

        Returns:
            Model metadata dictionary

        Raises:
            MLModelError: If metadata file not found or invalid
        """
        if MLService._metadata_cache is not None:
            return MLService._metadata_cache

        path = Path(settings.MODEL_METADATA_PATH)
        if not path.exists():
            msg = f"Metadata file not found: {settings.MODEL_METADATA_PATH}"
            logger.error(msg)
            raise MLModelError(msg)

        try:
            logger.info(f"Loading metadata from {path}")
            with open(path, "r") as f:
                metadata = json.load(f)
            MLService._metadata_cache = metadata
            logger.info("Successfully loaded model metadata")
            return metadata
        except json.JSONDecodeError as e:
            msg = f"Invalid JSON in metadata file: {str(e)}"
            logger.error(msg)
            raise MLModelError(msg)
        except Exception as e:
            msg = f"Failed to load metadata: {str(e)}"
            logger.error(msg)
            raise MLModelError(msg)

    @staticmethod
    def predict(
        features: list[float],
        model_name: str = "base",
    ) -> dict:
        """Make prediction using specified model.

        Args:
            features: Input features for prediction
            model_name: Model to use ("base" or "equipe")

        Returns:
            Dictionary with prediction and probabilities

        Raises:
            MLModelError: If prediction fails
        """
        try:
            model = MLService.load_model(model_name)
            metadata = MLService.load_metadata()

            # Prepare input
            X = np.array([features])

            # Make prediction
            prediction = model.predict(X)[0]
            probabilities = model.predict_proba(X)[0]
            classes = metadata.get("classes", [])

            logger.info(
                f"Prediction made with {model_name} model: {prediction}"
            )

            return {
                "prediction": prediction,
                "probabilities": {
                    cls: float(prob)
                    for cls, prob in zip(classes, probabilities)
                },
                "model_used": model_name,
            }
        except MLModelError:
            raise
        except Exception as e:
            msg = f"Prediction failed: {str(e)}"
            logger.error(msg)
            raise MLModelError(msg)

    @staticmethod
    def clear_cache() -> None:
        """Clear model cache (useful for model updates)."""
        MLService._model_cache.clear()
        MLService._metadata_cache = None
        logger.info("ML model cache cleared")
