"""Cart operation validation and business rules"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from ..models.core import Product, CartItem, EntityType
from ..interfaces import ProductSearchInterface


class ValidationError(Exception):
    """Custom exception for validation errors"""
    
    def __init__(self, message: str, suggestions: Optional[List[str]] = None):
        super().__init__(message)
        self.suggestions = suggestions or []


class CartValidator:
    """Validates cart operations and enforces business rules"""
    
    def __init__(self, product_search: ProductSearchInterface, 
                 max_cart_items: int = 50, max_item_quantity: int = 100):
        """Initialize cart validator
        
        Args:
            product_search: Product search interface for validation
            max_cart_items: Maximum total items in cart
            max_item_quantity: Maximum quantity per product
        """
        self.product_search = product_search
        self.max_cart_items = max_cart_items
        self.max_item_quantity = max_item_quantity
    
    def validate_add_operation(self, current_cart: List[CartItem], 
                             new_items: List[Dict[str, Any]]) -> Tuple[bool, str, List[str]]:
        """Validate adding items to cart
        
        Args:
            current_cart: Current cart items
            new_items: Items to be added
            
        Returns:
            Tuple of (is_valid, error_message, suggestions)
        """
        try:
            # Check cart size limits
            current_total = sum(item.quantity for item in current_cart)
            new_total = sum(item.get('quantity', 1) for item in new_items)
            
            if current_total + new_total > self.max_cart_items:
                suggestions = [
                    f"Remove some items from your cart (currently {current_total} items)",
                    f"Reduce quantities of items you're adding",
                    f"Add items in smaller batches"
                ]
                return False, f"Cart limit exceeded. Maximum {self.max_cart_items} items allowed.", suggestions
            
            # Validate each item
            for item_spec in new_items:
                is_valid, error_msg, item_suggestions = self._validate_item_spec(item_spec, current_cart)
                if not is_valid:
                    return False, error_msg, item_suggestions
            
            return True, "", []
            
        except Exception as e:
            return False, f"Validation error: {str(e)}", []
    
    def validate_remove_operation(self, current_cart: List[CartItem], 
                                criteria: Dict[str, Any]) -> Tuple[bool, str, List[str]]:
        """Validate removing items from cart
        
        Args:
            current_cart: Current cart items
            criteria: Removal criteria
            
        Returns:
            Tuple of (is_valid, error_message, suggestions)
        """
        try:
            if not current_cart:
                return False, "Your cart is empty", ["Add some items to your cart first"]
            
            # Check if criteria will match any items
            matching_items = []
            for item in current_cart:
                if self._matches_removal_criteria(item, criteria):
                    matching_items.append(item)
            
            if not matching_items:
                suggestions = self._generate_removal_suggestions(current_cart, criteria)
                return False, "No items found matching your criteria", suggestions
            
            return True, "", []
            
        except Exception as e:
            return False, f"Validation error: {str(e)}", []
    
    def validate_inventory_availability(self, product: Product, quantity: int, 
                                     size: Optional[str] = None, 
                                     color: Optional[str] = None) -> Tuple[bool, str, List[str]]:
        """Validate product inventory and availability
        
        Args:
            product: Product to validate
            quantity: Requested quantity
            size: Optional size requirement
            color: Optional color requirement
            
        Returns:
            Tuple of (is_valid, error_message, suggestions)
        """
        try:
            # Check if product is in stock
            if not product.in_stock:
                suggestions = self._find_similar_products(product)
                return False, f"{product.name} is currently out of stock", suggestions
            
            # Check size availability
            if size and not product.is_available_in_size(size):
                available_sizes = ", ".join(product.available_sizes) if product.available_sizes else "None"
                suggestions = [f"Available sizes: {available_sizes}"]
                return False, f"Size '{size}' is not available for {product.name}", suggestions
            
            # Check color availability
            if color and not product.is_available_in_color(color):
                available_colors = ", ".join(product.available_colors) if product.available_colors else "None"
                suggestions = [f"Available colors: {available_colors}"]
                return False, f"Color '{color}' is not available for {product.name}", suggestions
            
            # Check quantity limits
            if quantity > self.max_item_quantity:
                suggestions = [f"Maximum {self.max_item_quantity} items per product allowed"]
                return False, f"Quantity {quantity} exceeds maximum limit", suggestions
            
            return True, "", []
            
        except Exception as e:
            return False, f"Inventory validation error: {str(e)}", []
    
    def validate_price_constraints(self, items: List[Dict[str, Any]], 
                                 price_constraints: Optional[Dict[str, float]] = None) -> Tuple[bool, str, List[str]]:
        """Validate price constraints for cart items
        
        Args:
            items: Items to validate
            price_constraints: Optional price limits (min_price, max_price, budget)
            
        Returns:
            Tuple of (is_valid, error_message, suggestions)
        """
        if not price_constraints:
            return True, "", []
        
        try:
            total_cost = 0.0
            
            for item_spec in items:
                product = item_spec.get('product')
                quantity = item_spec.get('quantity', 1)
                
                if not isinstance(product, Product):
                    continue
                
                item_cost = product.price * quantity
                total_cost += item_cost
                
                # Check individual item price constraints
                if 'max_item_price' in price_constraints:
                    max_item_price = price_constraints['max_item_price']
                    if product.price > max_item_price:
                        suggestions = self._find_cheaper_alternatives(product, max_item_price)
                        return False, f"{product.name} (₹{product.price}) exceeds maximum item price of ₹{max_item_price}", suggestions
                
                if 'min_item_price' in price_constraints:
                    min_item_price = price_constraints['min_item_price']
                    if product.price < min_item_price:
                        suggestions = self._find_premium_alternatives(product, min_item_price)
                        return False, f"{product.name} (₹{product.price}) is below minimum item price of ₹{min_item_price}", suggestions
            
            # Check total budget constraint
            if 'budget' in price_constraints:
                budget = price_constraints['budget']
                if total_cost > budget:
                    suggestions = self._generate_budget_suggestions(items, budget, total_cost)
                    return False, f"Total cost ₹{total_cost:.2f} exceeds budget of ₹{budget:.2f}", suggestions
            
            return True, "", []
            
        except Exception as e:
            return False, f"Price validation error: {str(e)}", []
    
    def validate_business_rules(self, current_cart: List[CartItem], 
                              new_items: List[Dict[str, Any]]) -> Tuple[bool, str, List[str]]:
        """Validate business rules and constraints
        
        Args:
            current_cart: Current cart items
            new_items: Items to be added
            
        Returns:
            Tuple of (is_valid, error_message, suggestions)
        """
        try:
            # Rule: Maximum 5 different products per cart
            current_products = set(item.product.id for item in current_cart)
            new_products = set(item['product'].id for item in new_items if 'product' in item)
            total_products = len(current_products | new_products)
            
            if total_products > 5:
                suggestions = [
                    "Remove some products from your cart",
                    "Complete this purchase and start a new cart for additional items"
                ]
                return False, "Maximum 5 different products allowed per cart", suggestions
            
            # Rule: No duplicate items with same specifications
            for new_item in new_items:
                product = new_item.get('product')
                size = new_item.get('size')
                color = new_item.get('color')
                
                for cart_item in current_cart:
                    if (cart_item.product.id == product.id and
                        cart_item.size == size and
                        cart_item.color == color):
                        suggestions = [
                            f"Update quantity of existing {product.name} instead",
                            "Choose different size or color"
                        ]
                        return False, f"{product.name} with same specifications already in cart", suggestions
            
            return True, "", []
            
        except Exception as e:
            return False, f"Business rule validation error: {str(e)}", []
    
    def _validate_item_spec(self, item_spec: Dict[str, Any], 
                          current_cart: List[CartItem]) -> Tuple[bool, str, List[str]]:
        """Validate individual item specification
        
        Args:
            item_spec: Item specification to validate
            current_cart: Current cart for context
            
        Returns:
            Tuple of (is_valid, error_message, suggestions)
        """
        # Check required fields
        if 'product' not in item_spec:
            return False, "Product is required", []
        
        product = item_spec['product']
        if not isinstance(product, Product):
            return False, "Invalid product specification", []
        
        quantity = item_spec.get('quantity', 1)
        if not isinstance(quantity, int) or quantity <= 0:
            return False, "Quantity must be a positive integer", []
        
        size = item_spec.get('size')
        color = item_spec.get('color')
        
        # Validate inventory
        is_valid, error_msg, suggestions = self.validate_inventory_availability(
            product, quantity, size, color
        )
        if not is_valid:
            return False, error_msg, suggestions
        
        return True, "", []
    
    def _matches_removal_criteria(self, cart_item: CartItem, criteria: Dict[str, Any]) -> bool:
        """Check if cart item matches removal criteria"""
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
        
        return True
    
    def _generate_removal_suggestions(self, current_cart: List[CartItem], 
                                    criteria: Dict[str, Any]) -> List[str]:
        """Generate suggestions for removal criteria that don't match"""
        suggestions = []
        
        # List available products
        product_names = [item.product.name for item in current_cart]
        if product_names:
            suggestions.append(f"Available products: {', '.join(set(product_names))}")
        
        # List available colors if color was specified
        if 'color' in criteria:
            colors = [item.color for item in current_cart if item.color]
            if colors:
                suggestions.append(f"Available colors: {', '.join(set(colors))}")
        
        # List available sizes if size was specified
        if 'size' in criteria:
            sizes = [item.size for item in current_cart if item.size]
            if sizes:
                suggestions.append(f"Available sizes: {', '.join(set(sizes))}")
        
        return suggestions
    
    def _find_similar_products(self, product: Product) -> List[str]:
        """Find similar products when one is out of stock"""
        suggestions = []
        
        # Search for products in same category
        similar_products = self.product_search.search_products({
            'category': product.category,
            'in_stock': True,
            'limit': 3
        })
        
        if similar_products:
            names = [p.name for p in similar_products if p.id != product.id]
            if names:
                suggestions.append(f"Similar products available: {', '.join(names)}")
        
        return suggestions
    
    def _find_cheaper_alternatives(self, product: Product, max_price: float) -> List[str]:
        """Find cheaper alternatives to a product"""
        suggestions = []
        
        alternatives = self.product_search.search_products({
            'category': product.category,
            'price_max': max_price,
            'in_stock': True,
            'limit': 3
        })
        
        if alternatives:
            names = [f"{p.name} (₹{p.price})" for p in alternatives if p.id != product.id]
            if names:
                suggestions.append(f"Cheaper alternatives: {', '.join(names)}")
        
        return suggestions
    
    def _find_premium_alternatives(self, product: Product, min_price: float) -> List[str]:
        """Find premium alternatives to a product"""
        suggestions = []
        
        alternatives = self.product_search.search_products({
            'category': product.category,
            'price_min': min_price,
            'in_stock': True,
            'limit': 3
        })
        
        if alternatives:
            names = [f"{p.name} (₹{p.price})" for p in alternatives if p.id != product.id]
            if names:
                suggestions.append(f"Premium alternatives: {', '.join(names)}")
        
        return suggestions
    
    def _generate_budget_suggestions(self, items: List[Dict[str, Any]], 
                                   budget: float, current_total: float) -> List[str]:
        """Generate suggestions to fit within budget"""
        suggestions = []
        
        overage = current_total - budget
        suggestions.append(f"You're ₹{overage:.2f} over budget")
        
        # Suggest removing most expensive items
        item_costs = []
        for item_spec in items:
            product = item_spec.get('product')
            quantity = item_spec.get('quantity', 1)
            if product:
                cost = product.price * quantity
                item_costs.append((product.name, cost))
        
        if item_costs:
            item_costs.sort(key=lambda x: x[1], reverse=True)
            most_expensive = item_costs[0]
            suggestions.append(f"Consider removing {most_expensive[0]} (₹{most_expensive[1]:.2f})")
        
        # Suggest reducing quantities
        suggestions.append("Reduce quantities of items")
        
        return suggestions