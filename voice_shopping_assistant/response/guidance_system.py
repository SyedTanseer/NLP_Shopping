"""User guidance system for voice shopping assistant"""

from typing import List, Dict, Any, Optional
from ..models.core import Intent, IntentType, EntityType, Product, CartSummary
from ..nlp.conversation_context import ConversationContext


class GuidanceSystem:
    """Provides contextual guidance and help to users"""
    
    def __init__(self):
        """Initialize guidance system"""
        self.help_topics = self._initialize_help_topics()
        self.example_commands = self._initialize_example_commands()
        self.feature_explanations = self._initialize_feature_explanations()
    
    def _initialize_help_topics(self) -> Dict[str, List[str]]:
        """Initialize help topics and their explanations"""
        return {
            "adding_items": [
                "To add items to your cart, say 'Add [quantity] [product] to cart'",
                "You can specify details like 'Add 2 red t-shirts size medium to cart'",
                "Include brand names: 'Add Nike running shoes to cart'"
            ],
            "removing_items": [
                "To remove items, say 'Remove [product] from cart'",
                "Remove specific quantities: 'Remove 1 blue shirt from cart'",
                "Remove all of an item: 'Remove all t-shirts from cart'"
            ],
            "searching": [
                "Search for products by saying 'Search for [product]'",
                "Add filters: 'Search for red shoes under 2000 rupees'",
                "Search by category: 'Search for electronics' or 'Find books'"
            ],
            "checkout": [
                "When ready to buy, say 'Checkout' or 'Proceed to checkout'",
                "I'll show you your cart summary and total price",
                "Confirm your order to complete the purchase"
            ],
            "cart_management": [
                "Check your cart by saying 'Show my cart' or 'What's in my cart?'",
                "Clear your cart: 'Clear my cart' or 'Empty my cart'",
                "Get cart total: 'What's my total?' or 'How much is my cart?'"
            ],
            "product_details": [
                "Ask about availability: 'Is this available in blue?'",
                "Check sizes: 'What sizes are available?'",
                "Get price info: 'How much does this cost?'"
            ]
        }
    
    def _initialize_example_commands(self) -> Dict[str, List[str]]:
        """Initialize example commands for each intent type"""
        return {
            "add": [
                "Add 2 black t-shirts to cart",
                "Add Nike running shoes size 9 to cart",
                "Add 1 red dress medium size to cart",
                "Add wireless headphones to cart"
            ],
            "remove": [
                "Remove the blue jeans from cart",
                "Remove 1 t-shirt from cart",
                "Remove all shoes from cart",
                "Remove the last item I added"
            ],
            "search": [
                "Search for running shoes",
                "Find red dresses under 3000 rupees",
                "Search for Samsung phones",
                "Look for cotton t-shirts size large"
            ],
            "checkout": [
                "Checkout my cart",
                "Proceed to checkout",
                "I'm ready to buy",
                "Complete my order"
            ],
            "help": [
                "What can you do?",
                "How do I add items?",
                "Help me shop",
                "Show me commands"
            ]
        }
    
    def _initialize_feature_explanations(self) -> Dict[str, str]:
        """Initialize explanations for key features"""
        return {
            "voice_commands": "I understand natural voice commands for shopping. Speak clearly and include details like quantity, size, and color.",
            "product_search": "I can search our entire catalog. Use specific terms, brands, or describe what you're looking for.",
            "cart_management": "I keep track of your cart across the conversation. You can add, remove, and modify items anytime.",
            "smart_suggestions": "I'll suggest alternatives if items aren't available and help you find what you need.",
            "price_filtering": "Specify budgets like 'under 1000 rupees' or 'between 500 and 2000' when searching.",
            "size_color_options": "I'll show available sizes and colors for products. Just ask 'what sizes are available?'"
        }
    
    def generate_help_response(self, topic: str = None, context: ConversationContext = None) -> str:
        """Generate contextual help response
        
        Args:
            topic: Specific help topic requested
            context: Current conversation context
            
        Returns:
            Helpful guidance message
        """
        if topic and topic in self.help_topics:
            # Provide specific help for the requested topic
            help_items = self.help_topics[topic]
            return f"Here's how to {topic.replace('_', ' ')}: " + " ".join(help_items)
        
        # Provide general help based on context
        if context:
            cart_summary = context.get_cart_summary()
            last_intent = context.get_last_intent()
            
            # Contextual help based on current state
            if cart_summary and cart_summary.is_empty():
                return self._generate_empty_cart_help()
            elif cart_summary and cart_summary.total_items > 0:
                return self._generate_active_cart_help(cart_summary)
            elif last_intent and last_intent.type == IntentType.SEARCH:
                return self._generate_search_help()
            else:
                return self._generate_general_help()
        
        return self._generate_general_help()
    
    def _generate_empty_cart_help(self) -> str:
        """Generate help for users with empty carts"""
        return (
            "Your cart is empty. To get started, try saying: "
            "'Add [product] to cart', 'Search for [item]', or "
            "'Find [category] products'. For example: 'Add 2 t-shirts to cart' "
            "or 'Search for running shoes under 2000 rupees'."
        )
    
    def _generate_active_cart_help(self, cart_summary: CartSummary) -> str:
        """Generate help for users with items in cart"""
        item_count = cart_summary.total_items
        return (
            f"You have {item_count} items in your cart. You can: "
            "add more items ('Add [product] to cart'), "
            "remove items ('Remove [product] from cart'), "
            "check your cart ('Show my cart'), or "
            "proceed to checkout ('Checkout my cart')."
        )
    
    def _generate_search_help(self) -> str:
        """Generate help for search functionality"""
        return (
            "To search effectively, try: 'Search for [product name]', "
            "'Find [brand] products', or add filters like "
            "'Search for red shoes under 1500 rupees'. "
            "You can also browse categories by saying 'Show me electronics' or 'Find clothing'."
        )
    
    def _generate_general_help(self) -> str:
        """Generate general help overview"""
        return (
            "I can help you shop with voice commands. Try: "
            "'Add [item] to cart', 'Remove [item] from cart', "
            "'Search for [product]', 'Show my cart', or 'Checkout'. "
            "Be specific with quantities, sizes, and colors for best results."
        )
    
    def get_command_examples(self, intent_type: str, count: int = 3) -> List[str]:
        """Get example commands for a specific intent type
        
        Args:
            intent_type: Type of intent (add, remove, search, etc.)
            count: Number of examples to return
            
        Returns:
            List of example commands
        """
        examples = self.example_commands.get(intent_type, [])
        return examples[:count]
    
    def generate_onboarding_message(self) -> str:
        """Generate welcome message for new users"""
        return (
            "Welcome to voice shopping! I can help you find and buy products using voice commands. "
            "Try saying 'Add t-shirt to cart', 'Search for phones', or 'Show my cart'. "
            "Say 'help' anytime if you need assistance."
        )
    
    def generate_feature_explanation(self, feature: str) -> str:
        """Generate explanation for a specific feature
        
        Args:
            feature: Feature to explain
            
        Returns:
            Feature explanation
        """
        return self.feature_explanations.get(feature, "I don't have information about that feature.")
    
    def suggest_next_actions(self, context: ConversationContext) -> List[str]:
        """Suggest logical next actions based on current context
        
        Args:
            context: Current conversation context
            
        Returns:
            List of suggested actions
        """
        suggestions = []
        
        cart_summary = context.get_cart_summary()
        last_intent = context.get_last_intent()
        
        if not cart_summary or cart_summary.is_empty():
            suggestions.extend([
                "Search for products you need",
                "Add items to your cart",
                "Browse our categories"
            ])
        elif cart_summary.total_items > 0:
            suggestions.extend([
                "Add more items to your cart",
                "Review your cart contents",
                "Proceed to checkout"
            ])
        
        # Context-specific suggestions
        if last_intent:
            if last_intent.type == IntentType.SEARCH:
                suggestions.append("Add found items to your cart")
            elif last_intent.type == IntentType.ADD:
                suggestions.extend([
                    "Continue shopping",
                    "Check your cart total"
                ])
            elif last_intent.type == IntentType.REMOVE:
                suggestions.extend([
                    "Add replacement items",
                    "Continue with checkout"
                ])
        
        return suggestions[:3]  # Limit to 3 suggestions
    
    def generate_progress_feedback(self, context: ConversationContext) -> str:
        """Generate feedback about shopping progress
        
        Args:
            context: Current conversation context
            
        Returns:
            Progress feedback message
        """
        cart_summary = context.get_cart_summary()
        command_count = len(context.get_command_history())
        
        if not cart_summary or cart_summary.is_empty():
            if command_count > 3:
                return "You've been browsing for a while. Found anything you'd like to add to your cart?"
            else:
                return "Let's start shopping! What are you looking for today?"
        
        item_count = cart_summary.total_items
        total_price = cart_summary.total_price
        
        if item_count == 1:
            return f"Great start! You have 1 item in your cart (₹{total_price}). Want to add more or checkout?"
        elif item_count < 5:
            return f"Nice! You have {item_count} items (₹{total_price}). Continue shopping or ready to checkout?"
        else:
            return f"Your cart is getting full! {item_count} items totaling ₹{total_price}. Ready to checkout?"
    
    def generate_encouragement_message(self, situation: str) -> str:
        """Generate encouraging messages for different situations
        
        Args:
            situation: Current situation (first_add, large_cart, etc.)
            
        Returns:
            Encouraging message
        """
        messages = {
            "first_add": "Great choice! Your first item is in the cart.",
            "large_cart": "You're building quite a collection! Nice shopping.",
            "successful_search": "Perfect! I found exactly what you were looking for.",
            "cart_recovery": "No problem! I've fixed your cart as requested.",
            "checkout_ready": "Excellent! Your order is ready for checkout."
        }
        
        return messages.get(situation, "Great job! Keep going.")
    
    def detect_user_confusion(self, context: ConversationContext) -> Optional[str]:
        """Detect if user seems confused and suggest help
        
        Args:
            context: Current conversation context
            
        Returns:
            Confusion detection message or None
        """
        recent_commands = context.get_command_history()[-5:]  # Last 5 commands
        
        # Check for repeated failed attempts
        if len(recent_commands) >= 3:
            # Look for patterns indicating confusion
            help_requests = sum(1 for cmd in recent_commands if "help" in cmd.lower())
            if help_requests >= 2:
                return "It seems you might need some guidance. Let me help you get started with voice shopping."
        
        # Check for repeated similar commands
        if len(recent_commands) >= 3:
            similar_commands = 0
            for i in range(len(recent_commands) - 1):
                if self._commands_similar(recent_commands[i], recent_commands[i + 1]):
                    similar_commands += 1
            
            if similar_commands >= 2:
                return "I notice you're trying similar commands. Would you like me to explain how to phrase requests differently?"
        
        return None
    
    def _commands_similar(self, cmd1: str, cmd2: str) -> bool:
        """Check if two commands are similar (indicating possible confusion)"""
        # Simple similarity check - could be enhanced with more sophisticated NLP
        words1 = set(cmd1.lower().split())
        words2 = set(cmd2.lower().split())
        
        # If more than 70% of words overlap, consider similar
        if len(words1) == 0 or len(words2) == 0:
            return False
        
        overlap = len(words1.intersection(words2))
        total_unique = len(words1.union(words2))
        
        return overlap / total_unique > 0.7