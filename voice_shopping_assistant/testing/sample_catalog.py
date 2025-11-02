"""Sample product catalog for testing and development"""

from typing import List, Dict, Any
from ..models.core import Product


class SampleProductCatalog:
    """Sample product catalog with diverse items for testing"""
    
    def __init__(self):
        """Initialize the sample catalog"""
        self._products = self._create_sample_products()
    
    def get_all_products(self) -> List[Product]:
        """Get all products in the catalog"""
        return self._products.copy()
    
    def get_products_by_category(self, category: str) -> List[Product]:
        """Get products by category"""
        return [p for p in self._products if p.category.lower() == category.lower()]
    
    def get_product_by_id(self, product_id: str) -> Product:
        """Get product by ID"""
        for product in self._products:
            if product.id == product_id:
                return product
        raise ValueError(f"Product with ID '{product_id}' not found")
    
    def get_catalog_stats(self) -> Dict[str, Any]:
        """Get catalog statistics"""
        categories = {}
        brands = set()
        materials = set()
        colors = set()
        sizes = set()
        price_range = [float('inf'), 0]
        
        for product in self._products:
            # Count categories
            categories[product.category] = categories.get(product.category, 0) + 1
            
            # Collect unique values
            brands.add(product.brand)
            materials.add(product.material)
            colors.update(product.available_colors)
            sizes.update(product.available_sizes)
            
            # Track price range
            price_range[0] = min(price_range[0], product.price)
            price_range[1] = max(price_range[1], product.price)
        
        return {
            "total_products": len(self._products),
            "categories": dict(categories),
            "unique_brands": len(brands),
            "unique_materials": len(materials),
            "unique_colors": len(colors),
            "unique_sizes": len(sizes),
            "price_range": price_range,
            "in_stock_count": sum(1 for p in self._products if p.in_stock),
            "out_of_stock_count": sum(1 for p in self._products if not p.in_stock)
        }
    
    def _create_sample_products(self) -> List[Product]:
        """Create comprehensive sample product catalog"""
        products = []
        
        # Clothing items
        products.extend(self._create_clothing_products())
        
        # Electronics
        products.extend(self._create_electronics_products())
        
        # Home & Garden
        products.extend(self._create_home_garden_products())
        
        # Sports & Fitness
        products.extend(self._create_sports_products())
        
        # Books & Media
        products.extend(self._create_books_media_products())
        
        # Beauty & Personal Care
        products.extend(self._create_beauty_products())
        
        # Toys & Games
        products.extend(self._create_toys_games_products())
        
        # Food & Beverages
        products.extend(self._create_food_beverages_products())
        
        return products
    
    def _create_clothing_products(self) -> List[Product]:
        """Create clothing products covering various attributes"""
        return [
            # T-Shirts
            Product(
                id="tshirt-001",
                name="Classic Cotton T-Shirt",
                category="clothing",
                price=25.99,
                available_sizes=["XS", "S", "M", "L", "XL", "XXL"],
                available_colors=["white", "black", "red", "blue", "green"],
                material="cotton",
                brand="BasicWear",
                in_stock=True,
                description="Comfortable 100% cotton t-shirt perfect for everyday wear"
            ),
            Product(
                id="tshirt-002",
                name="Premium Organic T-Shirt",
                category="clothing",
                price=45.00,
                available_sizes=["S", "M", "L", "XL"],
                available_colors=["navy", "gray", "white"],
                material="organic cotton",
                brand="EcoFashion",
                in_stock=True,
                description="Sustainable organic cotton t-shirt with superior comfort"
            ),
            
            # Shirts
            Product(
                id="shirt-001",
                name="Formal Dress Shirt",
                category="clothing",
                price=89.99,
                available_sizes=["S", "M", "L", "XL", "XXL"],
                available_colors=["white", "light blue", "pink"],
                material="cotton blend",
                brand="BusinessPro",
                in_stock=True,
                description="Professional dress shirt perfect for office wear"
            ),
            Product(
                id="shirt-002",
                name="Casual Flannel Shirt",
                category="clothing",
                price=65.50,
                available_sizes=["M", "L", "XL"],
                available_colors=["red", "blue", "green", "gray"],
                material="flannel",
                brand="OutdoorStyle",
                in_stock=False,
                description="Cozy flannel shirt for casual outdoor activities"
            ),
            
            # Jeans & Pants
            Product(
                id="jeans-001",
                name="Classic Blue Jeans",
                category="clothing",
                price=79.99,
                available_sizes=["28", "30", "32", "34", "36", "38"],
                available_colors=["blue", "black", "gray"],
                material="denim",
                brand="DenimCraft",
                in_stock=True,
                description="Classic fit blue jeans made from premium denim"
            ),
            Product(
                id="pants-001",
                name="Formal Chino Pants",
                category="clothing",
                price=95.00,
                available_sizes=["30", "32", "34", "36"],
                available_colors=["khaki", "navy", "black", "gray"],
                material="cotton twill",
                brand="BusinessPro",
                in_stock=True,
                description="Versatile chino pants suitable for business casual"
            ),
            
            # Dresses
            Product(
                id="dress-001",
                name="Summer Floral Dress",
                category="clothing",
                price=120.00,
                available_sizes=["XS", "S", "M", "L"],
                available_colors=["floral blue", "floral pink", "floral yellow"],
                material="cotton blend",
                brand="SummerStyle",
                in_stock=True,
                description="Light and airy floral dress perfect for summer occasions"
            ),
            
            # Shoes
            Product(
                id="shoes-001",
                name="Running Sneakers",
                category="footwear",
                price=129.99,
                available_sizes=["7", "8", "9", "10", "11", "12"],
                available_colors=["white", "black", "blue", "red"],
                material="synthetic mesh",
                brand="SportMax",
                in_stock=True,
                description="Lightweight running shoes with excellent cushioning"
            ),
            Product(
                id="shoes-002",
                name="Leather Dress Shoes",
                category="footwear",
                price=199.99,
                available_sizes=["8", "9", "10", "11", "12"],
                available_colors=["black", "brown"],
                material="genuine leather",
                brand="ClassicStep",
                in_stock=True,
                description="Elegant leather dress shoes for formal occasions"
            ),
        ]
    
    def _create_electronics_products(self) -> List[Product]:
        """Create electronics products"""
        return [
            Product(
                id="phone-001",
                name="Smartphone Pro Max",
                category="electronics",
                price=999.99,
                available_sizes=["128GB", "256GB", "512GB"],
                available_colors=["black", "white", "blue", "red"],
                material="aluminum",
                brand="TechCorp",
                in_stock=True,
                description="Latest flagship smartphone with advanced camera system"
            ),
            Product(
                id="laptop-001",
                name="UltraBook Pro",
                category="electronics",
                price=1299.99,
                available_sizes=["13-inch", "15-inch"],
                available_colors=["silver", "space gray"],
                material="aluminum",
                brand="CompuTech",
                in_stock=True,
                description="High-performance laptop for professionals and creators"
            ),
            Product(
                id="headphones-001",
                name="Wireless Noise-Canceling Headphones",
                category="electronics",
                price=299.99,
                available_sizes=["one size"],
                available_colors=["black", "white", "blue"],
                material="plastic",
                brand="AudioMax",
                in_stock=True,
                description="Premium wireless headphones with active noise cancellation"
            ),
            Product(
                id="tablet-001",
                name="Tablet Air",
                category="electronics",
                price=599.99,
                available_sizes=["64GB", "128GB", "256GB"],
                available_colors=["silver", "gold", "rose gold"],
                material="aluminum",
                brand="TechCorp",
                in_stock=False,
                description="Lightweight tablet perfect for work and entertainment"
            ),
        ]
    
    def _create_home_garden_products(self) -> List[Product]:
        """Create home and garden products"""
        return [
            Product(
                id="sofa-001",
                name="3-Seater Fabric Sofa",
                category="furniture",
                price=899.99,
                available_sizes=["standard"],
                available_colors=["gray", "beige", "navy", "charcoal"],
                material="fabric",
                brand="ComfortHome",
                in_stock=True,
                description="Comfortable 3-seater sofa perfect for living rooms"
            ),
            Product(
                id="table-001",
                name="Dining Table Set",
                category="furniture",
                price=649.99,
                available_sizes=["4-seater", "6-seater"],
                available_colors=["oak", "walnut", "white"],
                material="wood",
                brand="WoodCraft",
                in_stock=True,
                description="Elegant dining table set with matching chairs"
            ),
            Product(
                id="lamp-001",
                name="Modern Floor Lamp",
                category="lighting",
                price=159.99,
                available_sizes=["standard"],
                available_colors=["black", "white", "brass"],
                material="metal",
                brand="LightDesign",
                in_stock=True,
                description="Stylish floor lamp with adjustable brightness"
            ),
            Product(
                id="plant-001",
                name="Indoor Plant Collection",
                category="garden",
                price=45.99,
                available_sizes=["small", "medium", "large"],
                available_colors=["green"],
                material="natural",
                brand="GreenThumb",
                in_stock=True,
                description="Beautiful collection of low-maintenance indoor plants"
            ),
        ]
    
    def _create_sports_products(self) -> List[Product]:
        """Create sports and fitness products"""
        return [
            Product(
                id="yoga-001",
                name="Premium Yoga Mat",
                category="sports",
                price=79.99,
                available_sizes=["standard"],
                available_colors=["purple", "blue", "pink", "black"],
                material="rubber",
                brand="YogaLife",
                in_stock=True,
                description="Non-slip yoga mat with excellent cushioning"
            ),
            Product(
                id="weights-001",
                name="Adjustable Dumbbells Set",
                category="sports",
                price=299.99,
                available_sizes=["5-50 lbs"],
                available_colors=["black"],
                material="steel",
                brand="FitnessPro",
                in_stock=True,
                description="Space-saving adjustable dumbbells for home workouts"
            ),
            Product(
                id="bike-001",
                name="Mountain Bike",
                category="sports",
                price=899.99,
                available_sizes=["S", "M", "L"],
                available_colors=["red", "blue", "black"],
                material="aluminum",
                brand="TrailRider",
                in_stock=False,
                description="Durable mountain bike for off-road adventures"
            ),
        ]
    
    def _create_books_media_products(self) -> List[Product]:
        """Create books and media products"""
        return [
            Product(
                id="book-001",
                name="Programming Fundamentals",
                category="books",
                price=49.99,
                available_sizes=["paperback", "hardcover"],
                available_colors=["standard"],
                material="paper",
                brand="TechBooks",
                in_stock=True,
                description="Comprehensive guide to programming fundamentals"
            ),
            Product(
                id="book-002",
                name="Cooking Masterclass",
                category="books",
                price=35.99,
                available_sizes=["paperback"],
                available_colors=["standard"],
                material="paper",
                brand="CulinaryPress",
                in_stock=True,
                description="Professional cooking techniques and recipes"
            ),
            Product(
                id="game-001",
                name="Strategy Board Game",
                category="games",
                price=59.99,
                available_sizes=["standard"],
                available_colors=["multicolor"],
                material="cardboard",
                brand="GameMasters",
                in_stock=True,
                description="Engaging strategy board game for 2-4 players"
            ),
        ]
    
    def _create_beauty_products(self) -> List[Product]:
        """Create beauty and personal care products"""
        return [
            Product(
                id="skincare-001",
                name="Anti-Aging Serum",
                category="beauty",
                price=89.99,
                available_sizes=["30ml", "50ml"],
                available_colors=["clear"],
                material="glass bottle",
                brand="SkinLux",
                in_stock=True,
                description="Advanced anti-aging serum with vitamin C"
            ),
            Product(
                id="makeup-001",
                name="Foundation Set",
                category="beauty",
                price=65.99,
                available_sizes=["standard"],
                available_colors=["light", "medium", "dark"],
                material="liquid",
                brand="BeautyPro",
                in_stock=True,
                description="Long-lasting foundation with natural coverage"
            ),
            Product(
                id="perfume-001",
                name="Luxury Fragrance",
                category="beauty",
                price=129.99,
                available_sizes=["50ml", "100ml"],
                available_colors=["clear"],
                material="glass",
                brand="FragranceLux",
                in_stock=False,
                description="Elegant fragrance with floral and woody notes"
            ),
        ]
    
    def _create_toys_games_products(self) -> List[Product]:
        """Create toys and games products"""
        return [
            Product(
                id="toy-001",
                name="Educational Building Blocks",
                category="toys",
                price=39.99,
                available_sizes=["100-piece", "200-piece"],
                available_colors=["multicolor"],
                material="plastic",
                brand="LearnPlay",
                in_stock=True,
                description="Creative building blocks for developing motor skills"
            ),
            Product(
                id="toy-002",
                name="Remote Control Car",
                category="toys",
                price=79.99,
                available_sizes=["standard"],
                available_colors=["red", "blue", "yellow"],
                material="plastic",
                brand="SpeedToys",
                in_stock=True,
                description="High-speed remote control car with rechargeable battery"
            ),
            Product(
                id="puzzle-001",
                name="1000-Piece Jigsaw Puzzle",
                category="toys",
                price=24.99,
                available_sizes=["1000-piece"],
                available_colors=["landscape", "animals", "abstract"],
                material="cardboard",
                brand="PuzzleMaster",
                in_stock=True,
                description="Challenging jigsaw puzzle with beautiful artwork"
            ),
        ]
    
    def _create_food_beverages_products(self) -> List[Product]:
        """Create food and beverage products"""
        return [
            Product(
                id="coffee-001",
                name="Premium Coffee Beans",
                category="food",
                price=24.99,
                available_sizes=["250g", "500g", "1kg"],
                available_colors=["dark roast", "medium roast", "light roast"],
                material="organic",
                brand="CoffeeCraft",
                in_stock=True,
                description="Freshly roasted premium coffee beans from single origin"
            ),
            Product(
                id="tea-001",
                name="Herbal Tea Collection",
                category="food",
                price=19.99,
                available_sizes=["20 bags", "40 bags"],
                available_colors=["chamomile", "peppermint", "green tea"],
                material="organic",
                brand="TeaGarden",
                in_stock=True,
                description="Soothing herbal tea collection with natural ingredients"
            ),
            Product(
                id="snacks-001",
                name="Organic Trail Mix",
                category="food",
                price=12.99,
                available_sizes=["200g", "500g"],
                available_colors=["mixed nuts", "tropical", "chocolate"],
                material="organic",
                brand="HealthySnacks",
                in_stock=True,
                description="Nutritious trail mix with nuts, dried fruits, and seeds"
            ),
        ]


# Global instance for easy access
sample_catalog = SampleProductCatalog()


def get_sample_products() -> List[Product]:
    """Get all sample products"""
    return sample_catalog.get_all_products()


def get_sample_product_by_id(product_id: str) -> Product:
    """Get sample product by ID"""
    return sample_catalog.get_product_by_id(product_id)


def get_sample_products_by_category(category: str) -> List[Product]:
    """Get sample products by category"""
    return sample_catalog.get_products_by_category(category)


def get_catalog_statistics() -> Dict[str, Any]:
    """Get sample catalog statistics"""
    return sample_catalog.get_catalog_stats()


def create_test_product_search():
    """Create a ProductSearch instance with sample data"""
    from ..cart.product_search import ProductSearch
    
    search = ProductSearch()
    search.update_product_catalog(get_sample_products())
    return search


def create_test_cart_manager():
    """Create a CartManager instance with sample product search"""
    from ..cart.cart_manager import CartManager
    
    product_search = create_test_product_search()
    return CartManager(product_search)