"""Response generator for voice shopping assistant"""

from typing import Optional, Dict, Any, List
from ..interfaces import ResponseGeneratorInterface, CartOperationResult
from ..models.core import Intent, IntentType, EntityType, CartSummary, Product
from ..nlp.conversation_context import ConversationContext
from .templates import ResponseTemplates
from .error_handler import ErrorHandler, ErrorType
from .guidance_system import GuidanceSystem


class ResponseGenerator(ResponseGeneratorInterface):
    """Generates appropriate responses for different cart operations and scenarios"""
    
    def __init__(self):
        """Initialize response generator"""
        self.templates = ResponseTemplates()
        self.error_handler = ErrorHandler()
        self.guidance_system = GuidanceSystem()
    
    def generate_response(self, intent: Intent, cart_result: Optional[CartOperationResult], 
                         context: ConversationContext) -> str:
        """Generate appropriate response text based on intent and cart operation result
        
        Args:
            intent: Classified intent with entities
            cart_result: Result of cart operation (if any)
            context: Conversation context
            
        Returns:
            Response text for user
        """
        try:
            if intent.type == IntentType.ADD:
                return self._generate_add_response(intent, cart_result, context)
            elif intent.type == IntentType.REMOVE:
                return self._generate_remove_response(intent, cart_result, context)
            elif intent.type == IntentType.SEARCH:
                return self._generate_search_response(intent, cart_result, context)
            elif intent.type == IntentType.CHECKOUT:
                return self._generate_checkout_response(intent, cart_result, context)
            elif intent.type == IntentType.HELP:
                return self._generate_help_response(intent, context)
            elif intent.type == IntentType.CANCEL:
                return self._generate_cancel_response(intent, context)
            else:
                return "I'm not sure how to help with that. Could you try rephrasing?"
        
        except Exception as e:
            return self.generate_error_response("response_generation", str(e))
    
    def _generate_add_response(self, intent: Intent, cart_result: Optional[CartOperationResult], 
                              context: ConversationContext) -> str:
        """Generate response for ADD intent"""
        if not cart_result:
            return "I couldn't process your add request. Please try again."
        
        if not cart_result.success:
            return f"Sorry, I couldn't add that item: {cart_result.message}"
        
        # Extract product details from entities
        product_entities = intent.get_entities_by_type(EntityType.PRODUCT)
        quantity_entities = intent.get_entities_by_type(EntityType.QUANTITY)
        color_entities = intent.get_entities_by_type(EntityType.COLOR)
        size_entities = intent.get_entities_by_type(EntityType.SIZE)
        
        product_name = product_entities[0].value if product_entities else "item"
        quantity = int(quantity_entities[0].value) if quantity_entities else 1
        color = color_entities[0].value if color_entities else None
        size = size_entities[0].value if size_entities else None
        
        # Get price from cart result if available
        price = None
        if cart_result.cart_summary and cart_result.cart_summary.items:
            # Find the most recently added item (assuming it's the last one)
            recent_item = cart_result.cart_summary.items[-1]
            price = recent_item.unit_price
        
        response = self.templates.format_add_success(
            quantity=quantity,
            product_name=product_name,
            color=color,
            size=size,
            price=price
        )
        
        # Add cart summary if requested or if cart is getting full
        if cart_result.cart_summary:
            if cart_result.cart_summary.total_items > 5:
                response += f" {self.templates.format_cart_summary(cart_result.cart_summary)}"
        
        return response
    
    def _generate_remove_response(self, intent: Intent, cart_result: Optional[CartOperationResult], 
                                 context: ConversationContext) -> str:
        """Generate response for REMOVE intent"""
        if not cart_result:
            return "I couldn't process your remove request. Please try again."
        
        if not cart_result.success:
            return f"Sorry, I couldn't remove that item: {cart_result.message}"
        
        # Extract product details from entities
        product_entities = intent.get_entities_by_type(EntityType.PRODUCT)
        quantity_entities = intent.get_entities_by_type(EntityType.QUANTITY)
        
        product_name = product_entities[0].value if product_entities else "item"
        
        # Determine if all items were removed or specific quantity
        removed_all = "all" in context.get_last_command().lower() if context.get_last_command() else False
        quantity = int(quantity_entities[0].value) if quantity_entities and not removed_all else 1
        
        response = self.templates.format_remove_success(
            quantity=quantity,
            product_name=product_name,
            removed_all=removed_all
        )
        
        # Add updated cart summary
        if cart_result.cart_summary:
            response += f" {self.templates.format_cart_summary(cart_result.cart_summary)}"
        
        return response
    
    def _generate_search_response(self, intent: Intent, cart_result: Optional[CartOperationResult], 
                                 context: ConversationContext) -> str:
        """Generate response for SEARCH intent"""
        # For search, cart_result might contain search results in a different format
        # We'll need to adapt this based on how search results are returned
        
        # Extract search criteria from entities
        search_criteria = []
        for entity in intent.entities:
            if entity.type in [EntityType.PRODUCT, EntityType.COLOR, EntityType.SIZE, 
                              EntityType.MATERIAL, EntityType.BRAND, EntityType.PRICE]:
                search_criteria.append(f"{entity.type.value}: {entity.value}")
        
        criteria_text = ", ".join(search_criteria) if search_criteria else "your criteria"
        
        # This is a placeholder - in real implementation, search results would be passed differently
        # For now, we'll generate a generic search response
        if cart_result and cart_result.success:
            return f"I found some products matching {criteria_text}. {cart_result.message}"
        else:
            return f"I searched for products matching {criteria_text}, but didn't find any results. Try different criteria or browse our categories."
    
    def _generate_checkout_response(self, intent: Intent, cart_result: Optional[CartOperationResult], 
                                   context: ConversationContext) -> str:
        """Generate response for CHECKOUT intent"""
        if not cart_result or not cart_result.cart_summary:
            return "I couldn't access your cart for checkout. Please try again."
        
        if cart_result.cart_summary.is_empty():
            return self.templates.format_checkout_summary(cart_result.cart_summary)
        
        # Generate detailed checkout summary
        checkout_response = self.templates.format_checkout_summary(cart_result.cart_summary)
        
        # Add detailed item breakdown for checkout
        detailed_summary = self.templates.format_detailed_cart_summary(cart_result.cart_summary)
        
        return f"{checkout_response} {detailed_summary}"
    
    def _generate_help_response(self, intent: Intent, context: ConversationContext) -> str:
        """Generate response for HELP intent"""
        # Check if user seems confused and provide targeted help
        confusion_message = self.guidance_system.detect_user_confusion(context)
        if confusion_message:
            return confusion_message
        
        # Generate contextual help based on current state
        return self.guidance_system.generate_help_response(context=context)
    
    def _generate_cancel_response(self, intent: Intent, context: ConversationContext) -> str:
        """Generate response for CANCEL intent"""
        return "Okay, I've cancelled that operation. What else can I help you with?"
    
    def generate_error_response(self, error_type: str, details: str) -> str:
        """Generate error response with helpful guidance
        
        Args:
            error_type: Type of error (asr_failure, nlp_ambiguity, etc.)
            details: Error details
            
        Returns:
            User-friendly error message with guidance
        """
        # Convert string error type to ErrorType enum
        try:
            error_enum = ErrorType(error_type)
        except ValueError:
            error_enum = ErrorType.NETWORK_ERROR  # Default fallback
        
        return self.error_handler.generate_error_message(error_enum, details)
    
    def generate_clarification_request(self, ambiguous_entities: List[str], 
                                     suggestions: List[str] = None) -> str:
        """Generate clarification request for ambiguous input
        
        Args:
            ambiguous_entities: List of ambiguous entity values
            suggestions: Optional list of suggestions
            
        Returns:
            Clarification request message
        """
        if len(ambiguous_entities) == 1:
            base_message = f"I found multiple matches for '{ambiguous_entities[0]}'"
        else:
            entities_text = "', '".join(ambiguous_entities)
            base_message = f"I found multiple matches for '{entities_text}'"
        
        if suggestions:
            suggestions_text = ", ".join(suggestions[:3])  # Limit to 3 suggestions
            return f"{base_message}. Did you mean: {suggestions_text}?"
        else:
            return f"{base_message}. Could you be more specific?"
    
    def generate_confirmation_request(self, action: str, details: Dict[str, Any]) -> str:
        """Generate confirmation request for important actions
        
        Args:
            action: Action to confirm (add, remove, checkout)
            details: Action details
            
        Returns:
            Confirmation request message
        """
        if action == "add":
            product = details.get("product", "item")
            quantity = details.get("quantity", 1)
            price = details.get("price")
            
            message = f"Add {quantity} {product}"
            if price:
                message += f" for ₹{price} each"
            message += " to your cart?"
            
        elif action == "remove":
            product = details.get("product", "item")
            quantity = details.get("quantity", "all")
            
            if quantity == "all":
                message = f"Remove all {product} from your cart?"
            else:
                message = f"Remove {quantity} {product} from your cart?"
                
        elif action == "checkout":
            total_items = details.get("total_items", 0)
            total_price = details.get("total_price", 0)
            message = f"Proceed to checkout with {total_items} items for ₹{total_price}?"
            
        else:
            message = f"Confirm {action}?"
        
        return message
    
    def generate_suggestion_response(self, suggestion_type: str, 
                                   products: List[Product] = None, 
                                   alternatives: List[str] = None) -> str:
        """Generate suggestion response for various scenarios
        
        Args:
            suggestion_type: Type of suggestion (alternative_products, price_range, etc.)
            products: List of suggested products
            alternatives: List of alternative suggestions
            
        Returns:
            Suggestion response message
        """
        if suggestion_type == "alternative_products" and products:
            return self.templates.format_product_suggestion(products, "alternative")
        
        elif suggestion_type == "similar_products" and products:
            return self.templates.format_product_suggestion(products, "similar")
        
        elif suggestion_type == "price_range" and products:
            if len(products) >= 2:
                prices = [p.price for p in products]
                min_price, max_price = min(prices), max(prices)
                return self.templates.format_price_range_info(min_price, max_price)
        
        elif suggestion_type == "search_alternatives" and alternatives:
            alt_text = ", ".join(alternatives[:3])
            return f"Try searching for: {alt_text}"
        
        elif suggestion_type == "category_browse":
            return "You can also browse our categories: clothing, electronics, home & garden, sports, or books."
        
        return "Let me know if you'd like to try something else."
    
    def generate_smart_error_response(self, intent: Intent, error_details: Dict[str, Any], 
                                    context: ConversationContext) -> str:
        """Generate intelligent error response with analysis and suggestions
        
        Args:
            intent: Failed intent
            error_details: Details about the error
            context: Conversation context
            
        Returns:
            Smart error response with guidance
        """
        # Analyze the intent for specific errors
        intent_errors = self.error_handler.analyze_intent_errors(intent)
        
        if intent_errors:
            primary_error = intent_errors[0]
            error_type = primary_error["type"]
            
            # Generate clarification questions if needed
            clarification_questions = self.error_handler.generate_clarification_questions(
                error_type, error_details
            )
            
            # Generate alternative suggestions
            alternatives = self.error_handler.generate_alternative_suggestions(
                error_type, error_details
            )
            
            # Combine error message with guidance
            base_message = self.error_handler.generate_error_message(
                error_type, primary_error["message"]
            )
            
            if clarification_questions:
                base_message += f" {clarification_questions[0]}"
            elif alternatives:
                alt_text = " Or ".join(alternatives[:2])
                base_message += f" {alt_text}"
            
            return base_message
        
        # Fallback to general error handling
        return self.generate_error_response("processing_error", "Unable to process your request")
    
    def generate_contextual_response(self, intent: Intent, cart_result: Optional[CartOperationResult], 
                                   context: ConversationContext) -> str:
        """Generate response with additional contextual information
        
        Args:
            intent: Processed intent
            cart_result: Cart operation result
            context: Conversation context
            
        Returns:
            Enhanced response with context
        """
        # Generate base response
        base_response = self.generate_response(intent, cart_result, context)
        
        # Add contextual enhancements
        enhancements = []
        
        # Add progress feedback for significant milestones
        if cart_result and cart_result.cart_summary:
            if cart_result.cart_summary.total_items == 1:
                enhancements.append(self.guidance_system.generate_encouragement_message("first_add"))
            elif cart_result.cart_summary.total_items >= 5:
                enhancements.append(self.guidance_system.generate_encouragement_message("large_cart"))
        
        # Suggest next actions
        suggestions = self.guidance_system.suggest_next_actions(context)
        if suggestions and len(suggestions) > 0:
            if intent.type in [IntentType.ADD, IntentType.REMOVE]:
                enhancements.append(f"You can also: {suggestions[0].lower()}")
        
        # Combine base response with enhancements
        if enhancements:
            return f"{base_response} {' '.join(enhancements)}"
        
        return base_response
    
    def handle_low_confidence_intent(self, intent: Intent, context: ConversationContext) -> str:
        """Handle intents with low confidence scores
        
        Args:
            intent: Low confidence intent
            context: Conversation context
            
        Returns:
            Response requesting clarification or confirmation
        """
        confidence = intent.confidence
        
        if confidence < 0.4:
            # Very low confidence - request complete rephrase
            return (
                "I'm not sure I understood that correctly. "
                "Could you please rephrase what you'd like to do? "
                f"{self.guidance_system.generate_help_response(context=context)}"
            )
        
        elif confidence < 0.7:
            # Medium confidence - request confirmation
            if intent.type == IntentType.ADD:
                product_entities = intent.get_entities_by_type(EntityType.PRODUCT)
                quantity_entities = intent.get_entities_by_type(EntityType.QUANTITY)
                
                product = product_entities[0].value if product_entities else "item"
                quantity = quantity_entities[0].value if quantity_entities else "1"
                
                return f"Did you want to add {quantity} {product} to your cart? Please confirm."
            
            elif intent.type == IntentType.REMOVE:
                product_entities = intent.get_entities_by_type(EntityType.PRODUCT)
                product = product_entities[0].value if product_entities else "item"
                
                return f"Did you want to remove {product} from your cart? Please confirm."
            
            elif intent.type == IntentType.SEARCH:
                return "I think you want to search for products. What specifically are you looking for?"
            
            elif intent.type == IntentType.CHECKOUT:
                return "Did you want to proceed to checkout? Please confirm."
        
        return "I'm not completely sure about that request. Could you confirm or rephrase?"
    
    def generate_proactive_guidance(self, context: ConversationContext) -> Optional[str]:
        """Generate proactive guidance based on user behavior patterns
        
        Args:
            context: Conversation context
            
        Returns:
            Proactive guidance message or None
        """
        # Check for user confusion
        confusion_message = self.guidance_system.detect_user_confusion(context)
        if confusion_message:
            return confusion_message
        
        # Generate progress feedback
        progress_message = self.guidance_system.generate_progress_feedback(context)
        
        # Only return proactive guidance occasionally to avoid being annoying
        command_count = len(context.get_command_history())
        if command_count % 5 == 0 and command_count > 0:  # Every 5th command
            return progress_message
        
        return None