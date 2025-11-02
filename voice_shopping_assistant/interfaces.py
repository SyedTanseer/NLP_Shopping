"""Base interfaces for all system components"""

from abc import ABC, abstractmethod
from typing import List, Iterator, Optional, Dict, Any, TYPE_CHECKING
from .models.core import (
    TranscriptionResult, NLPResult, Intent, Entity, Product, CartItem, 
    CartSummary, VoiceCommand, ProcessingResult
)

if TYPE_CHECKING:
    from .nlp.conversation_context import ConversationContext


class ASREngineInterface(ABC):
    """Interface for Automatic Speech Recognition engines"""
    
    @abstractmethod
    def transcribe(self, audio_data: bytes) -> TranscriptionResult:
        """Convert audio to text with confidence scores
        
        Args:
            audio_data: Raw audio bytes
            
        Returns:
            TranscriptionResult with text and confidence
        """
        pass
    
    @abstractmethod
    def transcribe_streaming(self, audio_stream) -> Iterator[TranscriptionResult]:
        """Real-time transcription for immediate feedback
        
        Args:
            audio_stream: Streaming audio input
            
        Yields:
            Partial transcription results
        """
        pass


class TextPreprocessorInterface(ABC):
    """Interface for text preprocessing"""
    
    @abstractmethod
    def normalize_text(self, text: str) -> str:
        """Normalize text for NLP processing
        
        Args:
            text: Raw transcribed text
            
        Returns:
            Normalized text ready for NLP
        """
        pass
    
    @abstractmethod
    def normalize_currency(self, text: str) -> str:
        """Normalize currency expressions"""
        pass
    
    @abstractmethod
    def normalize_numbers(self, text: str) -> str:
        """Convert number words to digits"""
        pass


class IntentClassifierInterface(ABC):
    """Interface for intent classification"""
    
    @abstractmethod
    def classify(self, text: str) -> Intent:
        """Classify text into intent with confidence
        
        Args:
            text: Preprocessed text
            
        Returns:
            Intent classification result
        """
        pass
    
    @abstractmethod
    def get_supported_intents(self) -> List[str]:
        """Get list of supported intent types"""
        pass


class EntityExtractorInterface(ABC):
    """Interface for entity extraction"""
    
    @abstractmethod
    def extract_entities(self, text: str) -> List[Entity]:
        """Extract entities from text
        
        Args:
            text: Input text
            
        Returns:
            List of extracted entities
        """
        pass
    
    @abstractmethod
    def get_supported_entities(self) -> List[str]:
        """Get list of supported entity types"""
        pass


# ConversationContext moved to nlp/conversation_context.py


class NLPProcessorInterface(ABC):
    """Interface for complete NLP processing"""
    
    @abstractmethod
    def process(self, text: str, context: 'ConversationContext') -> NLPResult:
        """Extract intent and entities from text
        
        Args:
            text: Input text
            context: Conversation context
            
        Returns:
            Complete NLP processing result
        """
        pass
    
    @abstractmethod
    def resolve_references(self, entities: List[Entity], context: 'ConversationContext') -> List[Entity]:
        """Resolve pronouns like 'the red one' to specific items
        
        Args:
            entities: Extracted entities
            context: Conversation context with cart state
            
        Returns:
            Resolved entities
        """
        pass


class ProductSearchInterface(ABC):
    """Interface for product search functionality"""
    
    @abstractmethod
    def search_products(self, filters: Dict[str, Any]) -> List[Product]:
        """Search products with filters
        
        Args:
            filters: Search criteria (name, category, price_range, etc.)
            
        Returns:
            List of matching products
        """
        pass
    
    @abstractmethod
    def get_product_by_id(self, product_id: str) -> Optional[Product]:
        """Get product by ID"""
        pass
    
    @abstractmethod
    def fuzzy_search(self, query: str, limit: int = 10) -> List[Product]:
        """Fuzzy search for products"""
        pass


class CartOperationResult:
    """Result of cart operations"""
    
    def __init__(self, success: bool, message: str, cart_summary: Optional[CartSummary] = None):
        self.success = success
        self.message = message
        self.cart_summary = cart_summary
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "success": self.success,
            "message": self.message,
            "cart_summary": self.cart_summary.to_dict() if self.cart_summary else None
        }


class CartManagerInterface(ABC):
    """Interface for shopping cart management"""
    
    @abstractmethod
    def add_items(self, session_id: str, items: List[Dict[str, Any]]) -> CartOperationResult:
        """Add products to cart with validation
        
        Args:
            session_id: User session identifier
            items: List of item specifications
            
        Returns:
            Cart operation result
        """
        pass
    
    @abstractmethod
    def remove_items(self, session_id: str, criteria: Dict[str, Any]) -> CartOperationResult:
        """Remove items matching criteria
        
        Args:
            session_id: User session identifier
            criteria: Removal criteria
            
        Returns:
            Cart operation result
        """
        pass
    
    @abstractmethod
    def get_cart_summary(self, session_id: str) -> Optional[CartSummary]:
        """Get current cart state and totals
        
        Args:
            session_id: User session identifier
            
        Returns:
            Current cart summary or None if empty
        """
        pass
    
    @abstractmethod
    def clear_cart(self, session_id: str) -> CartOperationResult:
        """Clear all items from cart"""
        pass


class ResponseGeneratorInterface(ABC):
    """Interface for response generation"""
    
    @abstractmethod
    def generate_response(self, intent: Intent, cart_result: Optional[CartOperationResult], 
                         context: 'ConversationContext') -> str:
        """Generate appropriate response text
        
        Args:
            intent: Classified intent
            cart_result: Result of cart operation
            context: Conversation context
            
        Returns:
            Response text for user
        """
        pass
    
    @abstractmethod
    def generate_error_response(self, error_type: str, details: str) -> str:
        """Generate error response with helpful guidance"""
        pass


class VoiceSynthesizerInterface(ABC):
    """Interface for text-to-speech synthesis"""
    
    @abstractmethod
    def synthesize(self, text: str) -> bytes:
        """Convert text to speech audio
        
        Args:
            text: Text to synthesize
            
        Returns:
            Audio data as bytes
        """
        pass
    
    @abstractmethod
    def synthesize_streaming(self, text: str) -> Iterator[bytes]:
        """Stream audio synthesis for real-time playback"""
        pass


class VoiceAssistantInterface(ABC):
    """Main interface for the complete voice assistant"""
    
    @abstractmethod
    def process_voice_command(self, voice_command: VoiceCommand) -> ProcessingResult:
        """Process complete voice command through the pipeline
        
        Args:
            voice_command: Voice input with audio data
            
        Returns:
            Complete processing result
        """
        pass
    
    @abstractmethod
    def process_text_command(self, text: str, session_id: str) -> ProcessingResult:
        """Process text command directly (for testing/debugging)
        
        Args:
            text: Text command
            session_id: User session identifier
            
        Returns:
            Complete processing result
        """
        pass