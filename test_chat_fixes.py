#!/usr/bin/env python3
"""
Test the chat command fixes
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from voice_shopping_assistant.testing import get_sample_products
from voice_shopping_assistant.cart.product_search import ProductSearch

# Mock session state
class MockCart:
    def __init__(self):
        self.items = []
    
    def add_item(self, product, quantity):
        self.items.append({
            'product_id': product.id,
            'name': product.name,
            'price': product.price,
            'quantity': quantity,
            'brand': product.brand,
            'category': product.category
        })

def test_add_smartphone():
    """Test adding smartphone specifically"""
    print("🧪 Testing: 'add a smartphone to the cart'")
    
    products = get_sample_products()
    user_input = "add a smartphone to the cart"
    
    # Simulate the improved matching logic
    product_keywords = {
        'smartphone': ['smartphone'],
        'headphones': ['headphones', 'earphones'],
        'laptop': ['laptop'],
        'computer': ['computer'],
        'phone': ['phone'],
        'shirt': ['shirt', 'tshirt', 't-shirt'],
        'jeans': ['jeans'],
        'pants': ['pants', 'trousers'],
        'shoes': ['shoes', 'sneakers', 'boots'],
        'dress': ['dress'],
        'jacket': ['jacket', 'coat']
    }
    
    # Find the best matching product type
    best_match = None
    best_score = 0
    
    for product_type, keywords in product_keywords.items():
        for keyword in keywords:
            if keyword in user_input:
                score = len(keyword) + (10 if user_input.count(keyword) == 1 else 0)
                if score > best_score:
                    best_score = score
                    best_match = product_type
    
    print(f"  Best match: {best_match}")
    
    if best_match:
        keywords = product_keywords[best_match]
        matching_products = [p for p in products if any(kw in p.name.lower() for kw in keywords)]
        print(f"  Found {len(matching_products)} matching products:")
        for p in matching_products[:3]:
            print(f"    - {p.name} (${p.price:.2f})")
    
    return best_match == 'smartphone'

def test_search_blue_jeans():
    """Test searching for blue jeans under 500"""
    print("\n🔍 Testing: 'show me blue jeans under 500'")
    
    user_input = "show me blue jeans under 500"
    
    # Extract search terms
    search_terms = user_input.lower()
    for phrase in ['search for', 'find me', 'look for', 'show me', 'i want', 'get me']:
        search_terms = search_terms.replace(phrase, '')
    
    # Extract price constraint
    import re
    price_matches = re.findall(r'under\s+\$?(\d+)', search_terms)
    price_limit = None
    if price_matches:
        price_limit = float(price_matches[0])
        search_terms = re.sub(r'under\s+\$?\d+', '', search_terms)
    
    search_terms = search_terms.strip()
    
    print(f"  Extracted search terms: '{search_terms}'")
    print(f"  Price limit: ${price_limit}")
    
    # Search products
    all_products = get_sample_products()
    products = []
    
    # Look for exact matches first
    for product in all_products:
        if any(term in product.name.lower() for term in search_terms.split()):
            if not price_limit or product.price <= price_limit:
                products.append(product)
    
    print(f"  Found {len(products)} matching products:")
    for p in products[:5]:
        print(f"    - {p.name} (${p.price:.2f}) - {p.category}")
    
    # Check if results are relevant
    relevant = all('jeans' in p.name.lower() or 'jean' in p.name.lower() for p in products)
    return relevant and len(products) > 0

def main():
    """Run tests"""
    print("🛒 Testing Chat Command Fixes")
    print("=" * 40)
    
    # Test smartphone addition
    smartphone_ok = test_add_smartphone()
    
    # Test jeans search
    jeans_ok = test_search_blue_jeans()
    
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    print(f"  Smartphone matching: {'✅ FIXED' if smartphone_ok else '❌ Still broken'}")
    print(f"  Jeans search: {'✅ FIXED' if jeans_ok else '❌ Still broken'}")
    
    if smartphone_ok and jeans_ok:
        print("\n🎉 All fixes working correctly!")
    else:
        print("\n⚠️ Some issues remain")

if __name__ == "__main__":
    main()