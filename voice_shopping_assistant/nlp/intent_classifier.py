"""DistilBERT-based intent classifier for shopping commands"""

import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
from transformers import pipeline
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
import time
from pathlib import Path

from ..interfaces import IntentClassifierInterface
from ..models.core import Intent, IntentType, Entity
from ..config.settings import get_settings


logger = logging.getLogger(__name__)


class DistilBERTIntentClassifier(IntentClassifierInterface):
    """DistilBERT-based intent classifier for shopping commands"""
    
    def __init__(self, model_path: Optional[str] = None, confidence_threshold: float = 0.8):
        """Initialize the intent classifier
        
        Args:
            model_path: Path to fine-tuned model or HuggingFace model name
            confidence_threshold: Minimum confidence for intent classification
        """
        self.settings = get_settings()
        self.model_path = model_path or self.settings.nlp.intent_model_path
        self.confidence_threshold = confidence_threshold or self.settings.nlp.intent_confidence_threshold
        
        # Intent mapping
        self.intent_labels = {
            0: IntentType.ADD,
            1: IntentType.REMOVE, 
            2: IntentType.SEARCH,
            3: IntentType.CHECKOUT,
            4: IntentType.HELP,
            5: IntentType.CANCEL
        }
        
        self.label_to_id = {v: k for k, v in self.intent_labels.items()}
        
        # Model components
        self.tokenizer = None
        self.model = None
        self.classifier_pipeline = None
        
        # Fallback patterns for rule-based classification
        self.fallback_patterns = {
            IntentType.ADD: [
                'add', 'put', 'include', 'want', 'need', 'buy', 'purchase', 
                'get me', 'i want', 'i need', 'add to cart', 'put in cart'
            ],
            IntentType.REMOVE: [
                'remove', 'delete', 'take out', 'cancel', 'dont want', 
                'remove from cart', 'take away', 'eliminate'
            ],
            IntentType.SEARCH: [
                'search', 'find', 'look for', 'show me', 'what do you have',
                'do you have', 'available', 'browse', 'explore'
            ],
            IntentType.CHECKOUT: [
                'checkout', 'pay', 'purchase', 'buy now', 'proceed to payment',
                'complete order', 'finish shopping', 'place order'
            ],
            IntentType.HELP: [
                'help', 'what can you do', 'how to', 'assist', 'support',
                'commands', 'options', 'guide'
            ],
            IntentType.CANCEL: [
                'cancel', 'stop', 'quit', 'exit', 'never mind', 'forget it',
                'abort', 'end'
            ]
        }
        
        self._load_model()
    
    def _load_model(self) -> None:
        """Load the DistilBERT model and tokenizer"""
        try:
            logger.info(f"Loading DistilBERT model from {self.model_path}")
            
            # Try to load fine-tuned model first
            if Path(self.model_path).exists():
                logger.info("Loading fine-tuned model from local path")
                self.tokenizer = DistilBertTokenizer.from_pretrained(self.model_path)
                self.model = DistilBertForSequenceClassification.from_pretrained(
                    self.model_path,
                    num_labels=len(self.intent_labels)
                )
            else:
                # Load base model and initialize for our task
                logger.info("Loading base DistilBERT model")
                self.tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
                self.model = DistilBertForSequenceClassification.from_pretrained(
                    'distilbert-base-uncased',
                    num_labels=len(self.intent_labels)
                )
            
            # Create classification pipeline
            self.classifier_pipeline = pipeline(
                "text-classification",
                model=self.model,
                tokenizer=self.tokenizer,
                return_all_scores=True
            )
            
            # Set model to evaluation mode
            self.model.eval()
            
            logger.info("DistilBERT intent classifier loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load DistilBERT model: {e}")
            logger.warning("Falling back to rule-based classification only")
            self.model = None
            self.tokenizer = None
            self.classifier_pipeline = None
    
    def classify(self, text: str) -> Intent:
        """Classify text into intent with confidence
        
        Args:
            text: Preprocessed text to classify
            
        Returns:
            Intent classification result
        """
        start_time = time.time()
        
        try:
            # Try DistilBERT classification first
            if self.classifier_pipeline is not None:
                intent = self._classify_with_distilbert(text)
                
                # If confidence is too low, try fallback
                if intent.confidence < self.confidence_threshold:
                    logger.debug(f"DistilBERT confidence {intent.confidence:.3f} below threshold, trying fallback")
                    fallback_intent = self._classify_with_fallback(text)
                    
                    # Use fallback if it has higher confidence
                    if fallback_intent.confidence > intent.confidence:
                        intent = fallback_intent
            else:
                # Use rule-based fallback only
                intent = self._classify_with_fallback(text)
            
            processing_time = time.time() - start_time
            logger.debug(f"Intent classification completed in {processing_time:.3f}s: {intent.type.value} ({intent.confidence:.3f})")
            
            return intent
            
        except Exception as e:
            logger.error(f"Intent classification failed: {e}")
            # Return low-confidence HELP intent as fallback
            return Intent(
                type=IntentType.HELP,
                confidence=0.1,
                entities=[]
            )
    
    def _classify_with_distilbert(self, text: str) -> Intent:
        """Classify using DistilBERT model
        
        Args:
            text: Input text
            
        Returns:
            Intent classification result
        """
        try:
            # Get predictions from pipeline
            results = self.classifier_pipeline(text)
            
            # Find the highest scoring intent
            best_result = max(results, key=lambda x: x['score'])
            
            # Map label to intent type
            try:
                if isinstance(best_result['label'], str):
                    if best_result['label'].startswith('LABEL_'):
                        label_id = int(best_result['label'].split('_')[-1])
                    else:
                        label_id = int(best_result['label'])
                else:
                    label_id = int(best_result['label'])
                intent_type = self.intent_labels.get(label_id, IntentType.HELP)
            except (ValueError, KeyError):
                # Fallback to help intent if label parsing fails
                intent_type = IntentType.HELP
            confidence = best_result['score']
            
            return Intent(
                type=intent_type,
                confidence=confidence,
                entities=[]  # Entities will be added by entity extractor
            )
            
        except Exception as e:
            logger.error(f"DistilBERT classification failed: {e}")
            return self._classify_with_fallback(text)
    
    def _classify_with_fallback(self, text: str) -> Intent:
        """Classify using rule-based patterns as fallback
        
        Args:
            text: Input text
            
        Returns:
            Intent classification result
        """
        text_lower = text.lower()
        intent_scores = {}
        
        # Score each intent based on pattern matches
        for intent_type, patterns in self.fallback_patterns.items():
            score = 0
            matches = 0
            
            for pattern in patterns:
                if pattern in text_lower:
                    # Longer patterns get higher scores
                    pattern_score = len(pattern.split()) * 0.2
                    score += pattern_score
                    matches += 1
            
            # Normalize score by number of patterns and text length
            if matches > 0:
                normalized_score = min(score / len(patterns), 1.0)
                intent_scores[intent_type] = normalized_score
        
        # Find best matching intent
        if intent_scores:
            best_intent = max(intent_scores.items(), key=lambda x: x[1])
            intent_type, confidence = best_intent
            
            # Apply minimum confidence threshold for fallback
            confidence = max(confidence, 0.3)  # Minimum fallback confidence
            
        else:
            # Default to HELP if no patterns match
            intent_type = IntentType.HELP
            confidence = 0.2
        
        return Intent(
            type=intent_type,
            confidence=confidence,
            entities=[]
        )
    
    def get_supported_intents(self) -> List[str]:
        """Get list of supported intent types
        
        Returns:
            List of intent type names
        """
        return [intent.value for intent in self.intent_labels.values()]
    
    def get_model_info(self) -> Dict[str, any]:
        """Get information about the loaded model
        
        Returns:
            Dictionary with model information
        """
        return {
            "model_path": self.model_path,
            "model_loaded": self.model is not None,
            "confidence_threshold": self.confidence_threshold,
            "supported_intents": self.get_supported_intents(),
            "fallback_available": True,
            "device": "cuda" if torch.cuda.is_available() and self.model is not None else "cpu"
        }
    
    def update_confidence_threshold(self, threshold: float) -> None:
        """Update confidence threshold for classification
        
        Args:
            threshold: New confidence threshold (0.0 to 1.0)
        """
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("Confidence threshold must be between 0.0 and 1.0")
        
        self.confidence_threshold = threshold
        logger.info(f"Updated confidence threshold to {threshold}")
    
    def batch_classify(self, texts: List[str]) -> List[Intent]:
        """Classify multiple texts in batch for efficiency
        
        Args:
            texts: List of texts to classify
            
        Returns:
            List of intent classification results
        """
        if not texts:
            return []
        
        results = []
        
        try:
            if self.classifier_pipeline is not None and len(texts) > 1:
                # Use pipeline for batch processing
                batch_results = self.classifier_pipeline(texts)
                
                for i, text_results in enumerate(batch_results):
                    best_result = max(text_results, key=lambda x: x['score'])
                    try:
                        if isinstance(best_result['label'], str):
                            if best_result['label'].startswith('LABEL_'):
                                label_id = int(best_result['label'].split('_')[-1])
                            else:
                                label_id = int(best_result['label'])
                        else:
                            label_id = int(best_result['label'])
                        intent_type = self.intent_labels.get(label_id, IntentType.HELP)
                    except (ValueError, KeyError):
                        intent_type = IntentType.HELP
                    confidence = best_result['score']
                    
                    # Apply fallback if confidence is low
                    if confidence < self.confidence_threshold:
                        fallback_intent = self._classify_with_fallback(texts[i])
                        if fallback_intent.confidence > confidence:
                            results.append(fallback_intent)
                        else:
                            results.append(Intent(type=intent_type, confidence=confidence, entities=[]))
                    else:
                        results.append(Intent(type=intent_type, confidence=confidence, entities=[]))
            else:
                # Process individually
                for text in texts:
                    results.append(self.classify(text))
                    
        except Exception as e:
            logger.error(f"Batch classification failed: {e}")
            # Fallback to individual processing
            for text in texts:
                results.append(self.classify(text))
        
        return results
    
    def validate_classification(self, text: str, expected_intent: IntentType) -> bool:
        """Validate classification against expected intent
        
        Args:
            text: Input text
            expected_intent: Expected intent type
            
        Returns:
            True if classification matches expected intent
        """
        result = self.classify(text)
        return result.type == expected_intent and result.confidence >= self.confidence_threshold


def create_intent_classifier(model_path: Optional[str] = None, 
                           confidence_threshold: Optional[float] = None) -> DistilBERTIntentClassifier:
    """Factory function to create intent classifier
    
    Args:
        model_path: Optional path to model
        confidence_threshold: Optional confidence threshold
        
    Returns:
        Configured intent classifier instance
    """
    return DistilBERTIntentClassifier(
        model_path=model_path,
        confidence_threshold=confidence_threshold
    )