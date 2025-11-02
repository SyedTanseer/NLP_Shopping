"""Natural Language Processing module for voice shopping assistant"""

from .intent_classifier import DistilBERTIntentClassifier, create_intent_classifier
from .training_data import (
    TrainingExample, 
    TrainingDataGenerator, 
    TrainingDataManager,
    create_training_dataset
)

__all__ = [
    'DistilBERTIntentClassifier',
    'create_intent_classifier',
    'TrainingExample',
    'TrainingDataGenerator', 
    'TrainingDataManager',
    'create_training_dataset'
]