"""Dependency injection for FastAPI endpoints"""

import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from functools import lru_cache

from ..interfaces import (
    VoiceAssistantInterface, CartManagerInterface, ProductSearchInterface,
    NLPProcessorInterface, ASREngineInterface, ResponseGeneratorInterface
)
from ..cart.cart_manager import CartManager
from ..cart.product_search import ProductSearch
from ..nlp.nlp_processor import create_nlp_processor
from ..asr.whisper_engine import create_asr_engine
from ..asr.text_preprocessor import TextPreprocessor
from ..response.response_generator import ResponseGenerator
from ..nlp.conversation_context import ConversationContext
from ..models.core import ProcessingResult, VoiceCommand, TranscriptionResult, NLPResult
from ..config.settings import get_settings


class VoiceAssistantService(VoiceAssistantInterface):
    """Main voice assistant service that coordinates all components"""
    
    def __init__(self):
        """Initialize voice assistant with all components"""
        self.settings = get_settings()
        
        # Initialize components
        self.asr_engine = create_asr_engine()
        self.text_preprocessor = TextPreprocessor()
        self.product_search = ProductSearch()
        self.cart_manager = CartManager(self.product_search)
        self.nlp_processor = create_nlp_processor()
        self.response_generator = ResponseGenerator()
        
        # Session contexts for conversation management
        self.session_contexts: Dict[str, ConversationContext] = {}
        
        print("Voice Assistant Service initialized successfully")
    
    def process_voice_command(self, voice_command: VoiceCommand) -> ProcessingResult:
        """Process complete voice command through the pipeline"""
        start_time = time.time()
        
        try:
            # Step 1: ASR - Convert audio to text
            transcription = self.asr_engine.transcribe(voice_command.audio_data)
            
            if not transcription.text or transcription.confidence < self.settings.asr.confidence_threshold:
                return self._create_error_result(
                    "I couldn't understand the audio clearly. Could you please try again?",
                    processing_time=time.time() - start_time
                )
            
            # Step 2: Process the transcribed text
            return self._process_text_internal(
                text=transcription.text,
                session_id=voice_command.session_id,
                start_time=start_time
            )
            
        except Exception as e:
            return self._create_error_result(
                f"Voice processing failed: {str(e)}",
                processing_time=time.time() - start_time
            )
    
    def process_text_command(self, text: str, session_id: str) -> ProcessingResult:
        """Process text command directly"""
        start_time = time.time()
        return self._process_text_internal(text, session_id, start_time)
    
    def _process_text_internal(self, text: str, session_id: str, start_time: float) -> ProcessingResult:
        """Internal text processing method"""
        try:
            # Step 1: Text preprocessing
            normalized_text = self.text_preprocessor.normalize_text(text)
            
            # Step 2: Get or create conversation context
            context = self._get_conversation_context(session_id)
            
            # Step 3: NLP processing
            nlp_result = self.nlp_processor.process(normalized_text, context)
            
            # Step 4: Execute cart operations based on intent
            cart_result = None
            if nlp_result.intent.type.value in ['add', 'remove', 'checkout']:
                cart_result = self._execute_cart_operation(nlp_result, session_id, context)
            
            # Step 5: Generate response
            response_text = self.response_generator.generate_response(
                nlp_result.intent, cart_result, context
            )
            
            # Step 6: Update conversation context
            context.add_command(text, nlp_result.intent, cart_result)
            
            # Step 7: Create processing result
            processing_time = time.time() - start_time
            
            result = ProcessingResult(
                original_text=text,
                normalized_text=normalized_text,
                intent=nlp_result.intent,
                entities=nlp_result.entities,
                response_text=response_text,
                confidence_score=nlp_result.confidence_score,
                processing_time=processing_time
            )
            
            return result
            
        except Exception as e:
            return self._create_error_result(
                f"Processing failed: {str(e)}",
                original_text=text,
                processing_time=time.time() - start_time
            )
    
    def _execute_cart_operation(self, nlp_result: NLPResult, session_id: str, context: ConversationContext):
        """Execute cart operations based on NLP result"""
        from ..models.core import IntentType, EntityType
        
        try:
            if nlp_result.intent.type == IntentType.ADD:
                return self._handle_add_intent(nlp_result, session_id, context)
            elif nlp_result.intent.type == IntentType.REMOVE:
                return self._handle_remove_intent(nlp_result, session_id, context)
            elif nlp_result.intent.type == IntentType.CHECKOUT:
                return self._handle_checkout_intent(nlp_result, session_id, context)
            
        except Exception as e:
            print(f"Cart operation failed: {e}")
            return None
    
    def _handle_add_intent(self, nlp_result: NLPResult, session_id: str, context: ConversationContext):
        """Handle ADD intent by adding items to cart"""
        from ..models.core import EntityType
        
        # Extract entities
        product_entities = nlp_result.intent.get_entities_by_type(EntityType.PRODUCT)
        quantity_entities = nlp_result.intent.get_entities_by_type(EntityType.QUANTITY)
        color_entities = nlp_result.intent.get_entities_by_type(EntityType.COLOR)
        size_entities = nlp_result.intent.get_entities_by_type(EntityType.SIZE)
        
        if not product_entities:
            return None
        
        # Search for products
        product_name = product_entities[0].value
        products = self.product_search.fuzzy_search(product_name, limit=1)
        
        if not products:
            return None
        
        # Create item specification
        quantity = 1
        if quantity_entities:
            try:
                quantity = int(quantity_entities[0].value)
            except ValueError:
                quantity = 1
        
        item_spec = {
            'product': products[0],
            'quantity': quantity,
            'size': size_entities[0].value if size_entities else None,
            'color': color_entities[0].value if color_entities else None
        }
        
        # Add to cart
        return self.cart_manager.add_items(session_id, [item_spec])
    
    def _handle_remove_intent(self, nlp_result: NLPResult, session_id: str, context: ConversationContext):
        """Handle REMOVE intent by removing items from cart"""
        from ..models.core import EntityType
        
        # Extract entities
        product_entities = nlp_result.intent.get_entities_by_type(EntityType.PRODUCT)
        color_entities = nlp_result.intent.get_entities_by_type(EntityType.COLOR)
        size_entities = nlp_result.intent.get_entities_by_type(EntityType.SIZE)
        
        # Create removal criteria
        criteria = {}
        if product_entities:
            criteria['product_name'] = product_entities[0].value
        if color_entities:
            criteria['color'] = color_entities[0].value
        if size_entities:
            criteria['size'] = size_entities[0].value
        
        # Remove from cart
        return self.cart_manager.remove_items(session_id, criteria)
    
    def _handle_checkout_intent(self, nlp_result: NLPResult, session_id: str, context: ConversationContext):
        """Handle CHECKOUT intent by getting cart summary"""
        # For checkout, we just return the current cart summary
        cart_summary = self.cart_manager.get_cart_summary(session_id)
        
        # Create a mock cart operation result for checkout
        from ..interfaces import CartOperationResult
        
        if cart_summary and not cart_summary.is_empty():
            return CartOperationResult(
                success=True,
                message=f"Ready to checkout {cart_summary.total_items} items for ₹{cart_summary.total_price:.2f}",
                cart_summary=cart_summary
            )
        else:
            return CartOperationResult(
                success=False,
                message="Your cart is empty. Add some items before checkout.",
                cart_summary=cart_summary
            )
    
    def _get_conversation_context(self, session_id: str) -> ConversationContext:
        """Get or create conversation context for session"""
        if session_id not in self.session_contexts:
            self.session_contexts[session_id] = ConversationContext(session_id)
        
        return self.session_contexts[session_id]
    
    def _create_error_result(self, error_message: str, original_text: str = "", processing_time: float = 0.0) -> ProcessingResult:
        """Create error processing result"""
        from ..models.core import Intent, IntentType
        
        error_intent = Intent(
            type=IntentType.HELP,
            confidence=0.0,
            entities=[]
        )
        
        return ProcessingResult(
            original_text=original_text,
            normalized_text=original_text.lower(),
            intent=error_intent,
            entities=[],
            response_text=error_message,
            confidence_score=0.0,
            processing_time=processing_time
        )


class SessionManager:
    """Manages user sessions and cleanup"""
    
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = timedelta(minutes=30)
    
    def update_session_activity(self, session_id: str):
        """Update session activity timestamp"""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                'created_at': datetime.now(),
                'last_activity': datetime.now()
            }
        else:
            self.sessions[session_id]['last_activity'] = datetime.now()
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Get session information"""
        if session_id not in self.sessions:
            return {
                'last_activity': datetime.now().isoformat(),
                'duration': 0.0
            }
        
        session = self.sessions[session_id]
        duration = (datetime.now() - session['created_at']).total_seconds()
        
        return {
            'last_activity': session['last_activity'].isoformat(),
            'duration': duration
        }
    
    def cleanup_expired_sessions(self):
        """Remove expired sessions"""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, session_data in self.sessions.items():
            if current_time - session_data['last_activity'] > self.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
        
        return len(expired_sessions)


class APIStats:
    """Tracks API usage statistics"""
    
    def __init__(self):
        self.start_time = time.time()
        self.total_requests = 0
        self.successful_requests = 0
        self.error_requests = 0
        self.processing_times = []
    
    def increment_request(self):
        """Increment total request counter"""
        self.total_requests += 1
    
    def increment_success(self):
        """Increment successful request counter"""
        self.successful_requests += 1
    
    def increment_error(self):
        """Increment error request counter"""
        self.error_requests += 1
    
    def record_processing_time(self, processing_time: float):
        """Record processing time"""
        self.processing_times.append(processing_time)
        # Keep only last 1000 processing times
        if len(self.processing_times) > 1000:
            self.processing_times = self.processing_times[-1000:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics"""
        avg_processing_time = 0.0
        if self.processing_times:
            avg_processing_time = sum(self.processing_times) / len(self.processing_times)
        
        return {
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'error_requests': self.error_requests,
            'average_processing_time': avg_processing_time,
            'uptime': time.time() - self.start_time
        }


# Global instances
_voice_assistant = None
_session_manager = None
_api_stats = None


@lru_cache()
def get_voice_processor() -> VoiceAssistantInterface:
    """Get voice processor instance"""
    global _voice_assistant
    if _voice_assistant is None:
        _voice_assistant = VoiceAssistantService()
    return _voice_assistant


@lru_cache()
def get_cart_manager() -> CartManagerInterface:
    """Get cart manager instance"""
    voice_processor = get_voice_processor()
    return voice_processor.cart_manager


@lru_cache()
def get_product_search() -> ProductSearchInterface:
    """Get product search instance"""
    voice_processor = get_voice_processor()
    return voice_processor.product_search


@lru_cache()
def get_session_manager() -> SessionManager:
    """Get session manager instance"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager


@lru_cache()
def get_api_stats() -> APIStats:
    """Get API stats instance"""
    global _api_stats
    if _api_stats is None:
        _api_stats = APIStats()
    return _api_stats


# Cleanup function for testing
def reset_dependencies():
    """Reset all dependencies (for testing)"""
    global _voice_assistant, _session_manager, _api_stats
    _voice_assistant = None
    _session_manager = None
    _api_stats = None
    
    # Clear LRU cache
    get_voice_processor.cache_clear()
    get_cart_manager.cache_clear()
    get_product_search.cache_clear()
    get_session_manager.cache_clear()
    get_api_stats.cache_clear()