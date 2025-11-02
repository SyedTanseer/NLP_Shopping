"""Response templates for different cart operations and scenarios"""

from typing import Dict, List, Any
from ..models.core import CartSummary, CartItem, Product, IntentType


class ResponseTemplates:
    """Template manager for generating consistent responses"""
    
    # Cart operation confirmation templates
    ADD_SUCCESS_TEMPLATES = [
        "Added {quantity} {product_name} to your cart.",
        "Great! I've added {quantity} {product_name} to your cart.",
        "Perfect! {quantity} {product_name} has been added to your cart.",
        "Done! Added {quantity} {product_name} to your cart."
    ]
    
    ADD_SUCCESS_WITH_DETAILS_TEMPLATES = [
        "Added {quantity} {product_name} in {color} {size} to your cart for ₹{price} each.",
        "Great! I've added {quantity} {color} {product_name} in size {size} to your cart.",
        "Perfect! {quantity} {color} {product_name} (size {size}) added for ₹{price} each."
    ]
    
    REMOVE_SUCCESS_TEMPLATES = [
        "Removed {quantity} {product_name} from your cart.",
        "Done! I've removed {quantity} {product_name} from your cart.",
        "Perfect! {quantity} {product_name} has been removed from your cart."
    ]
    
    REMOVE_ALL_SUCCESS_TEMPLATES = [
        "Removed all {product_name} from your cart.",
        "Done! All {product_name} items have been removed from your cart.",
        "Perfect! I've cleared all {product_name} from your cart."
    ]
    
    # Cart summary templates
    CART_SUMMARY_TEMPLATES = [
        "Your cart has {item_count} items totaling ₹{total_price}.",
        "You have {item_count} items in your cart for a total of ₹{total_price}.",
        "Your current cart: {item_count} items, total ₹{total_price}."
    ]
    
    CART_EMPTY_TEMPLATES = [
        "Your cart is empty.",
        "You don't have any items in your cart yet.",
        "Your cart is currently empty."
    ]
    
    # Search result templates
    SEARCH_RESULTS_TEMPLATES = [
        "I found {count} products matching your search:",
        "Here are {count} products I found for you:",
        "Found {count} items that match your criteria:"
    ]
    
    SEARCH_NO_RESULTS_TEMPLATES = [
        "I couldn't find any products matching your search criteria.",
        "No products found matching your requirements.",
        "Sorry, I didn't find any items that match what you're looking for."
    ]
    
    # Checkout templates
    CHECKOUT_SUMMARY_TEMPLATES = [
        "Ready to checkout? Your order has {item_count} items totaling ₹{total_price}.",
        "Here's your order summary: {item_count} items for ₹{total_price}. Shall I proceed?",
        "Your order: {item_count} items, total ₹{total_price}. Ready to checkout?"
    ]
    
    CHECKOUT_EMPTY_CART_TEMPLATES = [
        "Your cart is empty. Add some items before checkout.",
        "You need to add items to your cart before checking out.",
        "Please add some products to your cart first."
    ]
    
    # Confirmation templates
    CONFIRMATION_TEMPLATES = [
        "Is this correct?",
        "Does this look right?",
        "Shall I proceed?",
        "Would you like to continue?"
    ]
    
    @classmethod
    def format_add_success(cls, quantity: int, product_name: str, 
                          color: str = None, size: str = None, price: float = None) -> str:
        """Format successful add operation response"""
        if color and size and price:
            template = cls.ADD_SUCCESS_WITH_DETAILS_TEMPLATES[0]
            return template.format(
                quantity=quantity,
                product_name=product_name,
                color=color,
                size=size,
                price=price
            )
        else:
            template = cls.ADD_SUCCESS_TEMPLATES[0]
            return template.format(quantity=quantity, product_name=product_name)
    
    @classmethod
    def format_remove_success(cls, quantity: int, product_name: str, removed_all: bool = False) -> str:
        """Format successful remove operation response"""
        if removed_all:
            template = cls.REMOVE_ALL_SUCCESS_TEMPLATES[0]
            return template.format(product_name=product_name)
        else:
            template = cls.REMOVE_SUCCESS_TEMPLATES[0]
            return template.format(quantity=quantity, product_name=product_name)
    
    @classmethod
    def format_cart_summary(cls, cart_summary: CartSummary) -> str:
        """Format cart summary response"""
        if cart_summary.is_empty():
            return cls.CART_EMPTY_TEMPLATES[0]
        
        template = cls.CART_SUMMARY_TEMPLATES[0]
        return template.format(
            item_count=cart_summary.total_items,
            total_price=cart_summary.total_price
        )
    
    @classmethod
    def format_detailed_cart_summary(cls, cart_summary: CartSummary) -> str:
        """Format detailed cart summary with item breakdown"""
        if cart_summary.is_empty():
            return cls.CART_EMPTY_TEMPLATES[0]
        
        items_text = []
        for item in cart_summary.items:
            item_desc = f"{item.quantity} {item.product.name}"
            if item.color:
                item_desc += f" in {item.color}"
            if item.size:
                item_desc += f" (size {item.size})"
            item_desc += f" - ₹{item.total_price}"
            items_text.append(item_desc)
        
        items_list = ", ".join(items_text)
        return f"Your cart contains: {items_list}. Total: ₹{cart_summary.total_price}"
    
    @classmethod
    def format_search_results(cls, products: List[Product], query_info: str = "") -> str:
        """Format search results response"""
        if not products:
            return cls.SEARCH_NO_RESULTS_TEMPLATES[0]
        
        count = len(products)
        header = cls.SEARCH_RESULTS_TEMPLATES[0].format(count=count)
        
        product_list = []
        for i, product in enumerate(products[:5], 1):  # Limit to 5 results
            product_desc = f"{i}. {product.name} by {product.brand} - ₹{product.price}"
            if product.available_colors:
                product_desc += f" (Available in {', '.join(product.available_colors[:3])})"
            product_list.append(product_desc)
        
        return header + " " + "; ".join(product_list)
    
    @classmethod
    def format_checkout_summary(cls, cart_summary: CartSummary) -> str:
        """Format checkout summary response"""
        if cart_summary.is_empty():
            return cls.CHECKOUT_EMPTY_CART_TEMPLATES[0]
        
        template = cls.CHECKOUT_SUMMARY_TEMPLATES[0]
        return template.format(
            item_count=cart_summary.total_items,
            total_price=cart_summary.total_price
        )
    
    @classmethod
    def format_product_suggestion(cls, products: List[Product], reason: str = "") -> str:
        """Format product suggestions"""
        if not products:
            return "I don't have any suggestions at the moment."
        
        if len(products) == 1:
            product = products[0]
            return f"How about {product.name} by {product.brand} for ₹{product.price}?"
        
        suggestions = []
        for product in products[:3]:  # Limit to 3 suggestions
            suggestions.append(f"{product.name} (₹{product.price})")
        
        return f"You might like: {', '.join(suggestions)}"
    
    @classmethod
    def format_price_range_info(cls, min_price: float, max_price: float) -> str:
        """Format price range information"""
        return f"Prices range from ₹{min_price} to ₹{max_price}"
    
    @classmethod
    def format_availability_info(cls, product: Product) -> str:
        """Format product availability information"""
        info_parts = []
        
        if product.available_colors:
            colors = ", ".join(product.available_colors[:5])  # Limit to 5 colors
            info_parts.append(f"Available colors: {colors}")
        
        if product.available_sizes:
            sizes = ", ".join(product.available_sizes[:5])  # Limit to 5 sizes
            info_parts.append(f"Available sizes: {sizes}")
        
        stock_status = "In stock" if product.in_stock else "Out of stock"
        info_parts.append(stock_status)
        
        return ". ".join(info_parts)