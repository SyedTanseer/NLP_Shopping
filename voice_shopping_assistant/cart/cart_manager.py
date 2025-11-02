"""In-memory cart management implementation"""

import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import defaultdict

from ..interfaces import CartManagerInterface, CartOperationResult, ProductSearchInterface
from ..models.core import Product, CartItem, CartSummary, EntityType
from .validation import CartValidator


class CartManager(CartManagerInterface):
    """In-memory cart storage with session management"""
    
    def __init__(self, product_search: ProductSearchInterface, 
                 session_timeout_minutes: int = 30, max_cart_items: int = 50):
        """Initialize cart manager
        
        Args:
            product_search: Product search interface for validation
            session_timeout_minutes: Session timeout in minutes
            max_cart_items: Maximum items allowed per cart
        """
        self.session_timeout_minutes = session_timeout_minutes
        self.max_cart_items = max_cart_items
        
        # Initialize validator
        self.validator = CartValidator(product_search, max_cart_items)
        
        # Thread-safe storage for multiple user sessions
        self._carts: Dict[str, List[CartItem]] = defaultdict(list)
        self._session_timestamps: Dict[str, datetime] = {}
        self._lock = threading.RLock()
        
        # Start cleanup thread for expired sessions
        self._cleanup_thread = threading.Thread(target=self._cleanup_expired_sessions, daemon=True)
        self._cleanup_thread.start()
    
    def add_items(self, session_id: str, items: List[Dict[str, Any]]) -> CartOperationResult:
        """Add products to cart with validation
        
        Args:
            session_id: User session identifier
            items: List of item specifications with product, quantity, size, color
            
        Returns:
            Cart operation result with success status and updated cart
        """
        with self._lock:
            try:
                self._update_session_timestamp(session_id)
                
                # Validate input
                if not items:
                    return CartOperationResult(
                        success=False,
                        message="No items specified to add to cart"
                    )
                
                current_cart = self._carts[session_id]
                
                # Validate add operation
                is_valid, error_msg, suggestions = self.validator.validate_add_operation(current_cart, items)
                if not is_valid:
                    message = error_msg
                    if suggestions:
                        message += f" Suggestions: {'; '.join(suggestions)}"
                    return CartOperationResult(
                        success=False,
                        message=message
                    )
                
                added_items = []
                
                for item_spec in items:
                    try:
                        cart_item = self._create_cart_item_from_spec(item_spec)
                        
                        # Check if similar item already exists in cart
                        existing_item = self._find_similar_item(current_cart, cart_item)
                        
                        if existing_item:
                            # Update quantity of existing item
                            new_quantity = existing_item.quantity + cart_item.quantity
                            if new_quantity > 100:  # Business rule: max 100 per product
                                return CartOperationResult(
                                    success=False,
                                    message=f"Cannot add {cart_item.quantity} more {cart_item.product.name}. Maximum 100 per product."
                                )
                            existing_item.update_quantity(new_quantity)
                            added_items.append(f"{cart_item.quantity} more {cart_item.product.name}")
                        else:
                            # Add new item to cart
                            current_cart.append(cart_item)
                            added_items.append(f"{cart_item.quantity} {cart_item.product.name}")
                    
                    except ValueError as e:
                        return CartOperationResult(
                            success=False,
                            message=f"Invalid item specification: {str(e)}"
                        )
                
                cart_summary = self._create_cart_summary(session_id)
                
                if len(added_items) == 1:
                    message = f"Added {added_items[0]} to your cart"
                else:
                    message = f"Added {len(added_items)} items to your cart: {', '.join(added_items)}"
                
                return CartOperationResult(
                    success=True,
                    message=message,
                    cart_summary=cart_summary
                )
                
            except Exception as e:
                return CartOperationResult(
                    success=False,
                    message=f"Error adding items to cart: {str(e)}"
                )
    
    def remove_items(self, session_id: str, criteria: Dict[str, Any]) -> CartOperationResult:
        """Remove items matching criteria
        
        Args:
            session_id: User session identifier
            criteria: Removal criteria (product_name, color, size, quantity, etc.)
            
        Returns:
            Cart operation result with success status and updated cart
        """
        with self._lock:
            try:
                self._update_session_timestamp(session_id)
                
                current_cart = self._carts[session_id]
                
                # Validate remove operation
                is_valid, error_msg, suggestions = self.validator.validate_remove_operation(current_cart, criteria)
                if not is_valid:
                    message = error_msg
                    if suggestions:
                        message += f" Suggestions: {'; '.join(suggestions)}"
                    return CartOperationResult(
                        success=False,
                        message=message
                    )
                
                # Find items to remove based on criteria
                items_to_remove = []
                
                for i, cart_item in enumerate(current_cart):
                    if self._matches_removal_criteria(cart_item, criteria):
                        items_to_remove.append((i, cart_item))
                
                if not items_to_remove:
                    return CartOperationResult(
                        success=False,
                        message="No items found matching the removal criteria"
                    )
                
                # Remove items (in reverse order to maintain indices)
                removed_items = []
                for i, cart_item in reversed(items_to_remove):
                    removed_item = current_cart.pop(i)
                    removed_items.append(f"{removed_item.quantity} {removed_item.product.name}")
                
                cart_summary = self._create_cart_summary(session_id)
                
                if len(removed_items) == 1:
                    message = f"Removed {removed_items[0]} from your cart"
                else:
                    message = f"Removed {len(removed_items)} items from your cart: {', '.join(removed_items)}"
                
                return CartOperationResult(
                    success=True,
                    message=message,
                    cart_summary=cart_summary
                )
                
            except Exception as e:
                return CartOperationResult(
                    success=False,
                    message=f"Error removing items from cart: {str(e)}"
                )
    
    def get_cart_summary(self, session_id: str) -> Optional[CartSummary]:
        """Get current cart state and totals
        
        Args:
            session_id: User session identifier
            
        Returns:
            Current cart summary or None if empty
        """
        with self._lock:
            self._update_session_timestamp(session_id)
            
            if not self._carts[session_id]:
                return None
            
            return self._create_cart_summary(session_id)
    
    def clear_cart(self, session_id: str) -> CartOperationResult:
        """Clear all items from cart
        
        Args:
            session_id: User session identifier
            
        Returns:
            Cart operation result
        """
        with self._lock:
            try:
                self._update_session_timestamp(session_id)
                
                current_cart = self._carts[session_id]
                
                if not current_cart:
                    return CartOperationResult(
                        success=False,
                        message="Your cart is already empty"
                    )
                
                item_count = len(current_cart)
                current_cart.clear()
                
                return CartOperationResult(
                    success=True,
                    message=f"Cleared {item_count} items from your cart",
                    cart_summary=CartSummary.from_items([])
                )
                
            except Exception as e:
                return CartOperationResult(
                    success=False,
                    message=f"Error clearing cart: {str(e)}"
                )
    
    def update_item_quantity(self, session_id: str, product_id: str, new_quantity: int, 
                           size: Optional[str] = None, color: Optional[str] = None) -> CartOperationResult:
        """Update quantity of specific item in cart
        
        Args:
            session_id: User session identifier
            product_id: Product ID to update
            new_quantity: New quantity (0 to remove)
            size: Optional size specification
            color: Optional color specification
            
        Returns:
            Cart operation result
        """
        with self._lock:
            try:
                self._update_session_timestamp(session_id)
                
                current_cart = self._carts[session_id]
                
                # Find the specific item
                item_index = None
                for i, cart_item in enumerate(current_cart):
                    if (cart_item.product.id == product_id and
                        cart_item.size == size and
                        cart_item.color == color):
                        item_index = i
                        break
                
                if item_index is None:
                    return CartOperationResult(
                        success=False,
                        message="Item not found in cart"
                    )
                
                cart_item = current_cart[item_index]
                
                if new_quantity <= 0:
                    # Remove item
                    removed_item = current_cart.pop(item_index)
                    message = f"Removed {removed_item.product.name} from your cart"
                else:
                    # Update quantity
                    if new_quantity > 100:
                        return CartOperationResult(
                            success=False,
                            message="Maximum 100 items per product"
                        )
                    
                    old_quantity = cart_item.quantity
                    cart_item.update_quantity(new_quantity)
                    message = f"Updated {cart_item.product.name} quantity from {old_quantity} to {new_quantity}"
                
                cart_summary = self._create_cart_summary(session_id)
                
                return CartOperationResult(
                    success=True,
                    message=message,
                    cart_summary=cart_summary
                )
                
            except Exception as e:
                return CartOperationResult(
                    success=False,
                    message=f"Error updating item quantity: {str(e)}"
                )
    
    def get_session_count(self) -> int:
        """Get number of active sessions"""
        with self._lock:
            return len(self._carts)
    
    def validate_price_constraints(self, session_id: str, price_constraints: Dict[str, float]) -> CartOperationResult:
        """Validate current cart against price constraints
        
        Args:
            session_id: User session identifier
            price_constraints: Price limits (budget, max_item_price, etc.)
            
        Returns:
            Cart operation result with validation status
        """
        with self._lock:
            try:
                self._update_session_timestamp(session_id)
                
                current_cart = self._carts[session_id]
                
                if not current_cart:
                    return CartOperationResult(
                        success=True,
                        message="Cart is empty - no price constraints to validate"
                    )
                
                # Convert cart items to item specs for validation
                items = []
                for cart_item in current_cart:
                    items.append({
                        'product': cart_item.product,
                        'quantity': cart_item.quantity,
                        'size': cart_item.size,
                        'color': cart_item.color
                    })
                
                # Validate price constraints
                is_valid, error_msg, suggestions = self.validator.validate_price_constraints(items, price_constraints)
                
                if not is_valid:
                    message = error_msg
                    if suggestions:
                        message += f" Suggestions: {'; '.join(suggestions)}"
                    return CartOperationResult(
                        success=False,
                        message=message,
                        cart_summary=self._create_cart_summary(session_id)
                    )
                
                return CartOperationResult(
                    success=True,
                    message="Cart meets all price constraints",
                    cart_summary=self._create_cart_summary(session_id)
                )
                
            except Exception as e:
                return CartOperationResult(
                    success=False,
                    message=f"Error validating price constraints: {str(e)}"
                )
    
    def cleanup_session(self, session_id: str) -> bool:
        """Manually cleanup a specific session
        
        Args:
            session_id: Session to cleanup
            
        Returns:
            True if session was found and cleaned up
        """
        with self._lock:
            if session_id in self._carts:
                del self._carts[session_id]
                if session_id in self._session_timestamps:
                    del self._session_timestamps[session_id]
                return True
            return False
    
    def _create_cart_item_from_spec(self, item_spec: Dict[str, Any]) -> CartItem:
        """Create CartItem from specification dictionary
        
        Args:
            item_spec: Dictionary with product, quantity, size, color
            
        Returns:
            Validated CartItem instance
        """
        if 'product' not in item_spec:
            raise ValueError("Product is required in item specification")
        
        product = item_spec['product']
        if not isinstance(product, Product):
            raise ValueError("Product must be a Product instance")
        
        quantity = item_spec.get('quantity', 1)
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Quantity must be a positive integer")
        
        size = item_spec.get('size')
        color = item_spec.get('color')
        
        return CartItem(
            product=product,
            quantity=quantity,
            size=size,
            color=color
        )
    
    def _find_similar_item(self, cart: List[CartItem], new_item: CartItem) -> Optional[CartItem]:
        """Find existing cart item that matches product, size, and color
        
        Args:
            cart: Current cart items
            new_item: New item to check for similarity
            
        Returns:
            Existing similar item or None
        """
        for cart_item in cart:
            if (cart_item.product.id == new_item.product.id and
                cart_item.size == new_item.size and
                cart_item.color == new_item.color):
                return cart_item
        return None
    
    def _matches_removal_criteria(self, cart_item: CartItem, criteria: Dict[str, Any]) -> bool:
        """Check if cart item matches removal criteria
        
        Args:
            cart_item: Cart item to check
            criteria: Removal criteria
            
        Returns:
            True if item matches criteria
        """
        # Check product name/ID
        if 'product_name' in criteria:
            if criteria['product_name'].lower() not in cart_item.product.name.lower():
                return False
        
        if 'product_id' in criteria:
            if criteria['product_id'] != cart_item.product.id:
                return False
        
        # Check attributes
        if 'color' in criteria:
            if not cart_item.color or criteria['color'].lower() != cart_item.color.lower():
                return False
        
        if 'size' in criteria:
            if not cart_item.size or criteria['size'].lower() != cart_item.size.lower():
                return False
        
        # Check quantity (remove specific quantity or all)
        if 'quantity' in criteria:
            # This is handled by the caller - we just match the item
            pass
        
        # If no specific criteria, match all (for "remove everything" commands)
        if not any(key in criteria for key in ['product_name', 'product_id', 'color', 'size']):
            return True
        
        return True
    
    def _create_cart_summary(self, session_id: str) -> CartSummary:
        """Create cart summary for session
        
        Args:
            session_id: Session identifier
            
        Returns:
            CartSummary with current cart state
        """
        cart_items = self._carts[session_id]
        return CartSummary.from_items(cart_items)
    
    def _update_session_timestamp(self, session_id: str) -> None:
        """Update last activity timestamp for session
        
        Args:
            session_id: Session identifier
        """
        self._session_timestamps[session_id] = datetime.now()
    
    def _cleanup_expired_sessions(self) -> None:
        """Background thread to cleanup expired sessions"""
        while True:
            try:
                time.sleep(60)  # Check every minute
                
                with self._lock:
                    current_time = datetime.now()
                    expired_sessions = []
                    
                    for session_id, last_activity in self._session_timestamps.items():
                        if current_time - last_activity > timedelta(minutes=self.session_timeout_minutes):
                            expired_sessions.append(session_id)
                    
                    # Remove expired sessions
                    for session_id in expired_sessions:
                        if session_id in self._carts:
                            del self._carts[session_id]
                        del self._session_timestamps[session_id]
                
            except Exception:
                # Continue running even if cleanup fails
                pass