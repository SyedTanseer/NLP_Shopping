"""Error handling and user guidance for voice shopping assistant"""

from typing import Dict, List, Optional, Any
from enum import Enum
from ..models.core import Intent, Entity, Product, IntentType, EntityType


class ErrorType(Enum):
    """Types of errors that can occur in the system"""
    ASR_FAILURE = "asr_failure"
    NLP_AMBIGUITY = "nlp_ambiguity" 
    PRODUCT_NOT_FOUND = "product_not_found"
    INVALID_QUANTITY = "invalid_quantity"
    OUT_OF_STOCK = "out_of_stock"
    INVALID_SIZE_COLOR = "invalid_size_color"
    CART_LIMIT_EXCEEDED = "cart_limit_exceeded"
    EMPTY_CART = "empty_cart"
    NETWORK_ERROR = "network_error"
    PROCESSING_TIMEOUT = "processing_timeout"
    INVALID_PRICE_RANGE = "invalid_price_range"
    INSUFFICIENT_ENTITIES = "insufficient_entities"
    CONFLICTING_ENTITIES = "conflicting_entities"
    UNSUPPORTED_OPERATION = "unsupported_operation"


class ErrorHandler:
    """Handles errors and provides user guidance for recovery"""
    
    def __init__(self):
        """Initialize error handler with guidance templates"""
        self.error_messages = self._initialize_error_messages()
        self.recovery_suggestions = self._initialize_recovery_suggestions()
    
    def _initialize_error_messages(self) -> Dict[ErrorType, List[str]]:
        """Initialize error message templates for each error type"""
        return {
            ErrorType.ASR_FAILURE: [
                "I couldn't understand what you said clearly.",
                "I had trouble hearing you.",
                "Your audio wasn't clear enough for me to understand."
            ],
            ErrorType.NLP_AMBIGUITY: [
                "I'm not sure what you meant by that.",
                "That request was a bit unclear to me.",
                "I need more details to understand what you want."
            ],
            ErrorType.PRODUCT_NOT_FOUND: [
                "I couldn't find that product in our catalog.",
                "That item doesn't seem to be available.",
                "I don't have that product in stock right now."
            ],
            ErrorType.INVALID_QUANTITY: [
                "Please specify a valid quantity.",
                "I need a proper number for the quantity.",
                "The quantity you mentioned isn't valid."
            ],
            ErrorType.OUT_OF_STOCK: [
                "Sorry, that item is currently out of stock.",
                "That product isn't available right now.",
                "We're out of stock for that item."
            ],
            ErrorType.INVALID_SIZE_COLOR: [
                "That size or color isn't available for this product.",
                "We don't have that combination of size and color.",
                "That option isn't available for this item."
            ],
            ErrorType.CART_LIMIT_EXCEEDED: [
                "You've reached the maximum quantity for this item.",
                "That's too many of this product for one order.",
                "Please reduce the quantity - you've hit the limit."
            ],
            ErrorType.EMPTY_CART: [
                "Your cart is empty.",
                "You don't have any items in your cart yet.",
                "Add some products to your cart first."
            ],
            ErrorType.NETWORK_ERROR: [
                "I'm having trouble connecting right now.",
                "There's a network issue on my end.",
                "I can't reach our servers at the moment."
            ],
            ErrorType.PROCESSING_TIMEOUT: [
                "That request took too long to process.",
                "The operation timed out.",
                "I couldn't complete that in time."
            ],
            ErrorType.INVALID_PRICE_RANGE: [
                "That price range doesn't make sense.",
                "Please specify a valid price range.",
                "The price limits you mentioned aren't valid."
            ],
            ErrorType.INSUFFICIENT_ENTITIES: [
                "I need more information to complete that request.",
                "Please provide more details about what you want.",
                "That request is missing some important details."
            ],
            ErrorType.CONFLICTING_ENTITIES: [
                "The information you provided seems contradictory.",
                "I found conflicting details in your request.",
                "Some parts of your request don't match up."
            ],
            ErrorType.UNSUPPORTED_OPERATION: [
                "I can't perform that operation.",
                "That's not something I can help with.",
                "I don't support that type of request."
            ]
        }
    
    def _initialize_recovery_suggestions(self) -> Dict[ErrorType, List[str]]:
        """Initialize recovery suggestions for each error type"""
        return {
            ErrorType.ASR_FAILURE: [
                "Please speak more clearly and try again.",
                "Make sure you're in a quiet environment and repeat your request.",
                "Try speaking a bit slower and more distinctly."
            ],
            ErrorType.NLP_AMBIGUITY: [
                "Could you be more specific about what you want?",
                "Try rephrasing your request with more details.",
                "Please clarify what product or action you're looking for."
            ],
            ErrorType.PRODUCT_NOT_FOUND: [
                "Try searching with different keywords.",
                "Check the spelling or use alternative product names.",
                "Browse our categories to find similar items."
            ],
            ErrorType.INVALID_QUANTITY: [
                "Say a number like 'one', 'two', or '3'.",
                "Specify how many items you want (e.g., '2 shirts').",
                "Use clear numbers for quantities."
            ],
            ErrorType.OUT_OF_STOCK: [
                "Would you like me to suggest similar products?",
                "I can notify you when this item is back in stock.",
                "Let me show you alternative options."
            ],
            ErrorType.INVALID_SIZE_COLOR: [
                "Let me show you the available options for this product.",
                "Would you like to see what sizes and colors are available?",
                "Try a different size or color combination."
            ],
            ErrorType.CART_LIMIT_EXCEEDED: [
                "The maximum quantity for this item is 10 pieces.",
                "Try reducing the quantity or splitting into multiple orders.",
                "Contact customer service for bulk orders."
            ],
            ErrorType.EMPTY_CART: [
                "Start by saying 'add [product] to cart'.",
                "Browse our products and add items you like.",
                "Try searching for products you want to buy."
            ],
            ErrorType.NETWORK_ERROR: [
                "Please try again in a few moments.",
                "Check your internet connection and retry.",
                "The issue should resolve shortly."
            ],
            ErrorType.PROCESSING_TIMEOUT: [
                "Please try your request again.",
                "Simplify your request and try once more.",
                "Break down complex requests into smaller parts."
            ],
            ErrorType.INVALID_PRICE_RANGE: [
                "Use format like 'under 1000 rupees' or 'between 500 and 2000'.",
                "Specify minimum and maximum prices clearly.",
                "Try 'cheap', 'expensive', or specific amounts."
            ],
            ErrorType.INSUFFICIENT_ENTITIES: [
                "Tell me the product name and quantity you want.",
                "Include details like size, color, or brand if needed.",
                "Be more specific about what you're looking for."
            ],
            ErrorType.CONFLICTING_ENTITIES: [
                "Please clarify which option you prefer.",
                "Restate your request with consistent information.",
                "Choose one option and try again."
            ],
            ErrorType.UNSUPPORTED_OPERATION: [
                "Try 'add to cart', 'remove from cart', 'search', or 'checkout'.",
                "I can help with shopping, searching, and cart management.",
                "Ask for 'help' to see what I can do."
            ]
        }
    
    def generate_error_message(self, error_type: ErrorType, context: str = "", 
                              suggestions: List[str] = None) -> str:
        """Generate user-friendly error message with guidance
        
        Args:
            error_type: Type of error that occurred
            context: Additional context about the error
            suggestions: Optional specific suggestions
            
        Returns:
            Complete error message with guidance
        """
        # Get base error message
        base_messages = self.error_messages.get(error_type, ["Something went wrong."])
        base_message = base_messages[0]
        
        # Add context if provided
        if context:
            base_message += f" {context}"
        
        # Get recovery suggestions
        if suggestions:
            suggestion_text = " ".join(suggestions[:2])  # Limit to 2 suggestions
        else:
            recovery_suggestions = self.recovery_suggestions.get(error_type, [])
            suggestion_text = recovery_suggestions[0] if recovery_suggestions else "Please try again."
        
        return f"{base_message} {suggestion_text}"
    
    def analyze_intent_errors(self, intent: Intent) -> List[Dict[str, Any]]:
        """Analyze intent for potential errors and issues
        
        Args:
            intent: Intent to analyze
            
        Returns:
            List of error descriptions with suggested fixes
        """
        errors = []
        
        # Check confidence level
        if intent.confidence < 0.6:
            errors.append({
                "type": ErrorType.NLP_AMBIGUITY,
                "message": f"Low confidence ({intent.confidence:.2f}) in understanding your request",
                "suggestion": "Try rephrasing more clearly"
            })
        
        # Check for missing required entities
        required_entities = self._get_required_entities(intent.type)
        missing_entities = []
        
        for required_type in required_entities:
            if not intent.has_entity_type(required_type):
                missing_entities.append(required_type.value)
        
        if missing_entities:
            errors.append({
                "type": ErrorType.INSUFFICIENT_ENTITIES,
                "message": f"Missing required information: {', '.join(missing_entities)}",
                "suggestion": f"Please specify {', '.join(missing_entities)}"
            })
        
        # Check for conflicting entities
        conflicts = self._detect_entity_conflicts(intent.entities)
        if conflicts:
            errors.append({
                "type": ErrorType.CONFLICTING_ENTITIES,
                "message": f"Conflicting information: {conflicts}",
                "suggestion": "Please clarify which option you prefer"
            })
        
        return errors
    
    def _get_required_entities(self, intent_type: IntentType) -> List[EntityType]:
        """Get required entities for each intent type"""
        requirements = {
            IntentType.ADD: [EntityType.PRODUCT, EntityType.QUANTITY],
            IntentType.REMOVE: [EntityType.PRODUCT],
            IntentType.SEARCH: [EntityType.PRODUCT],  # At least one search criterion
            IntentType.CHECKOUT: [],  # No specific requirements
            IntentType.HELP: [],
            IntentType.CANCEL: []
        }
        return requirements.get(intent_type, [])
    
    def _detect_entity_conflicts(self, entities: List[Entity]) -> str:
        """Detect conflicting entities in the list
        
        Args:
            entities: List of entities to check
            
        Returns:
            Description of conflicts found, empty string if none
        """
        conflicts = []
        
        # Check for multiple conflicting quantities
        quantities = [e for e in entities if e.type == EntityType.QUANTITY]
        if len(quantities) > 1:
            values = [e.value for e in quantities]
            conflicts.append(f"multiple quantities: {', '.join(values)}")
        
        # Check for multiple conflicting prices
        prices = [e for e in entities if e.type == EntityType.PRICE]
        if len(prices) > 1:
            values = [e.value for e in prices]
            conflicts.append(f"multiple prices: {', '.join(values)}")
        
        # Check for multiple conflicting sizes
        sizes = [e for e in entities if e.type == EntityType.SIZE]
        if len(sizes) > 1:
            values = [e.value for e in sizes]
            conflicts.append(f"multiple sizes: {', '.join(values)}")
        
        # Check for multiple conflicting colors
        colors = [e for e in entities if e.type == EntityType.COLOR]
        if len(colors) > 1:
            values = [e.value for e in colors]
            conflicts.append(f"multiple colors: {', '.join(values)}")
        
        return "; ".join(conflicts)
    
    def generate_clarification_questions(self, error_type: ErrorType, 
                                       context: Dict[str, Any]) -> List[str]:
        """Generate clarification questions for specific errors
        
        Args:
            error_type: Type of error requiring clarification
            context: Context information for generating questions
            
        Returns:
            List of clarification questions
        """
        questions = []
        
        if error_type == ErrorType.NLP_AMBIGUITY:
            if "products" in context:
                products = context["products"][:3]  # Limit to 3 options
                product_names = [p.name for p in products]
                questions.append(f"Did you mean: {', '.join(product_names)}?")
            else:
                questions.append("Could you be more specific about what you're looking for?")
        
        elif error_type == ErrorType.INVALID_SIZE_COLOR:
            product = context.get("product")
            if product:
                if product.available_sizes:
                    sizes = ", ".join(product.available_sizes[:5])
                    questions.append(f"Available sizes are: {sizes}. Which would you like?")
                if product.available_colors:
                    colors = ", ".join(product.available_colors[:5])
                    questions.append(f"Available colors are: {colors}. Which would you prefer?")
        
        elif error_type == ErrorType.INSUFFICIENT_ENTITIES:
            missing = context.get("missing_entities", [])
            if "quantity" in missing:
                questions.append("How many would you like?")
            if "product" in missing:
                questions.append("What product are you looking for?")
            if "size" in missing:
                questions.append("What size do you need?")
            if "color" in missing:
                questions.append("What color would you prefer?")
        
        elif error_type == ErrorType.CONFLICTING_ENTITIES:
            conflicts = context.get("conflicts", "")
            if "quantities" in conflicts:
                questions.append("How many items do you want exactly?")
            if "sizes" in conflicts:
                questions.append("Which size would you prefer?")
            if "colors" in conflicts:
                questions.append("Which color would you like?")
        
        return questions
    
    def generate_alternative_suggestions(self, error_type: ErrorType, 
                                       context: Dict[str, Any]) -> List[str]:
        """Generate alternative suggestions for error recovery
        
        Args:
            error_type: Type of error
            context: Context for generating suggestions
            
        Returns:
            List of alternative suggestions
        """
        suggestions = []
        
        if error_type == ErrorType.PRODUCT_NOT_FOUND:
            query = context.get("query", "")
            if query:
                # Generate alternative search terms
                suggestions.extend([
                    f"Try searching for '{query}' in different categories",
                    f"Look for similar products to '{query}'",
                    "Browse our featured products instead"
                ])
        
        elif error_type == ErrorType.OUT_OF_STOCK:
            product = context.get("product")
            if product:
                suggestions.extend([
                    f"Get notified when {product.name} is back in stock",
                    f"Find similar products to {product.name}",
                    f"Check {product.brand} alternatives"
                ])
        
        elif error_type == ErrorType.INVALID_PRICE_RANGE:
            suggestions.extend([
                "Try 'under 1000 rupees'",
                "Say 'between 500 and 2000 rupees'",
                "Use 'cheap' or 'expensive' instead"
            ])
        
        elif error_type == ErrorType.CART_LIMIT_EXCEEDED:
            suggestions.extend([
                "Reduce the quantity to 10 or less",
                "Split your order into multiple purchases",
                "Contact customer service for bulk orders"
            ])
        
        return suggestions
    
    def should_request_confirmation(self, error_type: ErrorType, 
                                  confidence: float = 0.0) -> bool:
        """Determine if confirmation should be requested before proceeding
        
        Args:
            error_type: Type of error
            confidence: Confidence level of the operation
            
        Returns:
            True if confirmation should be requested
        """
        # Always confirm for potentially destructive operations
        destructive_errors = [
            ErrorType.CART_LIMIT_EXCEEDED,
            ErrorType.INVALID_SIZE_COLOR
        ]
        
        if error_type in destructive_errors:
            return True
        
        # Confirm for low confidence operations
        if confidence < 0.7:
            return True
        
        # Confirm for ambiguous operations
        ambiguous_errors = [
            ErrorType.NLP_AMBIGUITY,
            ErrorType.CONFLICTING_ENTITIES
        ]
        
        return error_type in ambiguous_errors