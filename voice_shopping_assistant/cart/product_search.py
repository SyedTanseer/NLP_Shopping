"""Product search functionality with filtering and fuzzy matching"""

import re
from typing import Dict, List, Optional, Any, Tuple
from difflib import SequenceMatcher
from collections import defaultdict

from ..interfaces import ProductSearchInterface
from ..models.core import Product


class ProductSearch(ProductSearchInterface):
    """Product search with filtering, fuzzy matching, and ranking"""
    
    def __init__(self, products: Optional[List[Product]] = None):
        """Initialize product search
        
        Args:
            products: Initial product catalog (can be updated later)
        """
        self.products: List[Product] = products or []
        self._build_search_indices()
    
    def add_products(self, products: List[Product]) -> None:
        """Add products to the catalog
        
        Args:
            products: List of products to add
        """
        self.products.extend(products)
        self._build_search_indices()
    
    def update_product_catalog(self, products: List[Product]) -> None:
        """Replace entire product catalog
        
        Args:
            products: New product catalog
        """
        self.products = products
        self._build_search_indices()
    
    def search_products(self, filters: Dict[str, Any]) -> List[Product]:
        """Search products with filters
        
        Args:
            filters: Search criteria including:
                - name: Product name (fuzzy match)
                - category: Product category
                - price_min: Minimum price
                - price_max: Maximum price
                - price_range: Tuple of (min, max) price
                - color: Available color
                - size: Available size
                - material: Product material
                - brand: Product brand
                - in_stock: Stock availability (boolean)
                - limit: Maximum results to return
                
        Returns:
            List of matching products, ranked by relevance
        """
        if not self.products:
            return []
        
        # Start with all products
        candidates = self.products.copy()
        
        # Apply filters
        candidates = self._apply_filters(candidates, filters)
        
        # Apply fuzzy name matching if specified
        if 'name' in filters:
            candidates = self._apply_fuzzy_name_search(candidates, filters['name'])
        
        # Rank results by relevance
        candidates = self._rank_results(candidates, filters)
        
        # Apply limit
        limit = filters.get('limit', 50)
        return candidates[:limit]
    
    def get_product_by_id(self, product_id: str) -> Optional[Product]:
        """Get product by ID
        
        Args:
            product_id: Product identifier
            
        Returns:
            Product if found, None otherwise
        """
        for product in self.products:
            if product.id == product_id:
                return product
        return None
    
    def fuzzy_search(self, query: str, limit: int = 10) -> List[Product]:
        """Fuzzy search for products by name and description
        
        Args:
            query: Search query
            limit: Maximum results to return
            
        Returns:
            List of products ranked by similarity
        """
        if not query.strip():
            return []
        
        query_lower = query.lower().strip()
        scored_products = []
        
        for product in self.products:
            # Calculate similarity scores
            name_score = self._calculate_similarity(query_lower, product.name.lower())
            category_score = self._calculate_similarity(query_lower, product.category.lower())
            brand_score = self._calculate_similarity(query_lower, product.brand.lower())
            
            # Check description if available
            desc_score = 0.0
            if product.description:
                desc_score = self._calculate_similarity(query_lower, product.description.lower())
            
            # Weighted overall score
            overall_score = (
                name_score * 0.5 +           # Name is most important
                category_score * 0.2 +       # Category is moderately important
                brand_score * 0.2 +          # Brand is moderately important
                desc_score * 0.1             # Description is least important
            )
            
            # Boost score for exact word matches
            if any(word in product.name.lower() for word in query_lower.split()):
                overall_score += 0.2
            
            # Only include products with reasonable similarity
            if overall_score > 0.3:
                scored_products.append((product, overall_score))
        
        # Sort by score (descending) and return top results
        scored_products.sort(key=lambda x: x[1], reverse=True)
        return [product for product, score in scored_products[:limit]]
    
    def search_by_attributes(self, **attributes) -> List[Product]:
        """Search products by specific attributes
        
        Args:
            **attributes: Attribute filters (color, size, material, brand, etc.)
            
        Returns:
            List of matching products
        """
        return self.search_products(attributes)
    
    def get_products_in_price_range(self, min_price: float, max_price: float) -> List[Product]:
        """Get products within price range
        
        Args:
            min_price: Minimum price (inclusive)
            max_price: Maximum price (inclusive)
            
        Returns:
            List of products in price range
        """
        return self.search_products({
            'price_min': min_price,
            'price_max': max_price
        })
    
    def get_available_filters(self) -> Dict[str, List[str]]:
        """Get available filter values from current catalog
        
        Returns:
            Dictionary of filter types and their available values
        """
        filters = {
            'categories': list(set(p.category for p in self.products)),
            'brands': list(set(p.brand for p in self.products)),
            'materials': list(set(p.material for p in self.products)),
            'colors': list(set(color for p in self.products for color in p.available_colors)),
            'sizes': list(set(size for p in self.products for size in p.available_sizes)),
        }
        
        # Sort all filter values
        for key in filters:
            filters[key].sort()
        
        return filters
    
    def get_price_range(self) -> Tuple[float, float]:
        """Get price range of all products
        
        Returns:
            Tuple of (min_price, max_price)
        """
        if not self.products:
            return (0.0, 0.0)
        
        prices = [p.price for p in self.products]
        return (min(prices), max(prices))
    
    def suggest_alternatives(self, filters: Dict[str, Any], max_suggestions: int = 5) -> List[Product]:
        """Suggest alternative products when search returns no results
        
        Args:
            filters: Original search filters
            max_suggestions: Maximum suggestions to return
            
        Returns:
            List of alternative products
        """
        # Try relaxing filters one by one
        relaxed_filters = filters.copy()
        
        # Remove most restrictive filters first
        filter_priority = ['color', 'size', 'material', 'price_max', 'price_min', 'brand']
        
        for filter_key in filter_priority:
            if filter_key in relaxed_filters:
                del relaxed_filters[filter_key]
                results = self.search_products(relaxed_filters)
                if results:
                    return results[:max_suggestions]
        
        # If still no results, try fuzzy search on name/category
        if 'name' in filters:
            return self.fuzzy_search(filters['name'], max_suggestions)
        
        # Last resort: return popular products (by category if specified)
        if 'category' in filters:
            category_products = [p for p in self.products if p.category.lower() == filters['category'].lower()]
            return category_products[:max_suggestions]
        
        # Return first few products as fallback
        return self.products[:max_suggestions]
    
    def _build_search_indices(self) -> None:
        """Build search indices for faster lookups"""
        # Build category index
        self._category_index = defaultdict(list)
        for product in self.products:
            self._category_index[product.category.lower()].append(product)
        
        # Build brand index
        self._brand_index = defaultdict(list)
        for product in self.products:
            self._brand_index[product.brand.lower()].append(product)
        
        # Build material index
        self._material_index = defaultdict(list)
        for product in self.products:
            self._material_index[product.material.lower()].append(product)
    
    def _apply_filters(self, products: List[Product], filters: Dict[str, Any]) -> List[Product]:
        """Apply all filters to product list
        
        Args:
            products: List of products to filter
            filters: Filter criteria
            
        Returns:
            Filtered product list
        """
        filtered = products
        
        # Category filter
        if 'category' in filters:
            category = filters['category'].lower()
            filtered = [p for p in filtered if p.category.lower() == category]
        
        # Brand filter
        if 'brand' in filters:
            brand = filters['brand'].lower()
            filtered = [p for p in filtered if p.brand.lower() == brand]
        
        # Material filter
        if 'material' in filters:
            material = filters['material'].lower()
            filtered = [p for p in filtered if p.material.lower() == material]
        
        # Price filters
        if 'price_min' in filters:
            min_price = float(filters['price_min'])
            filtered = [p for p in filtered if p.price >= min_price]
        
        if 'price_max' in filters:
            max_price = float(filters['price_max'])
            filtered = [p for p in filtered if p.price <= max_price]
        
        if 'price_range' in filters:
            min_price, max_price = filters['price_range']
            filtered = [p for p in filtered if min_price <= p.price <= max_price]
        
        # Color filter
        if 'color' in filters:
            color = filters['color'].lower()
            filtered = [p for p in filtered if p.is_available_in_color(color)]
        
        # Size filter
        if 'size' in filters:
            size = filters['size'].lower()
            filtered = [p for p in filtered if p.is_available_in_size(size)]
        
        # Stock filter
        if 'in_stock' in filters:
            in_stock = bool(filters['in_stock'])
            filtered = [p for p in filtered if p.in_stock == in_stock]
        
        return filtered
    
    def _apply_fuzzy_name_search(self, products: List[Product], query: str) -> List[Product]:
        """Apply fuzzy name matching to products
        
        Args:
            products: List of products to search
            query: Search query
            
        Returns:
            Products matching the query with similarity scores
        """
        query_lower = query.lower().strip()
        scored_products = []
        
        for product in products:
            # Calculate name similarity
            name_similarity = self._calculate_similarity(query_lower, product.name.lower())
            
            # Boost for exact word matches
            query_words = query_lower.split()
            name_words = product.name.lower().split()
            
            exact_matches = sum(1 for word in query_words if word in name_words)
            word_boost = exact_matches * 0.2
            
            total_score = name_similarity + word_boost
            
            # Only include products with reasonable similarity
            if total_score > 0.4:
                scored_products.append((product, total_score))
        
        # Sort by score and return products
        scored_products.sort(key=lambda x: x[1], reverse=True)
        return [product for product, score in scored_products]
    
    def _rank_results(self, products: List[Product], filters: Dict[str, Any]) -> List[Product]:
        """Rank search results by relevance
        
        Args:
            products: List of products to rank
            filters: Original search filters
            
        Returns:
            Ranked product list
        """
        # For now, simple ranking by stock status and price
        def rank_key(product):
            score = 0
            
            # Prioritize in-stock products
            if product.in_stock:
                score += 1000
            
            # Prefer lower prices (negative to sort ascending)
            score -= product.price
            
            return score
        
        return sorted(products, key=rank_key, reverse=True)
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings
        
        Args:
            text1: First text string
            text2: Second text string
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        return SequenceMatcher(None, text1, text2).ratio()
    
    def _normalize_text_for_search(self, text: str) -> str:
        """Normalize text for search operations
        
        Args:
            text: Input text
            
        Returns:
            Normalized text
        """
        # Convert to lowercase and remove extra whitespace
        text = text.lower().strip()
        
        # Remove special characters but keep spaces
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text