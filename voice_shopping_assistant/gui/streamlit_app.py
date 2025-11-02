"""
Streamlit GUI for Voice Shopping Assistant

A modern web interface for interacting with the voice shopping assistant,
including text input, product browsing, cart management, and testing tools.
"""

import streamlit as st
import streamlit.components.v1
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Import voice shopping assistant components
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from voice_shopping_assistant.testing import (
    get_sample_products, get_catalog_statistics,
    create_test_product_search, create_test_cart_manager,
    EndToEndTestRunner, ScenarioBuilder, run_end_to_end_tests
)
from voice_shopping_assistant.models.core import Product, CartSummary
from voice_shopping_assistant.cart.product_search import ProductSearch


# Page configuration
st.set_page_config(
    page_title="Voice Shopping Assistant",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .product-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: #f9f9f9;
    }
    .cart-item {
        border-left: 4px solid #1f77b4;
        padding-left: 1rem;
        margin: 0.5rem 0;
    }
    .success-message {
        color: #28a745;
        font-weight: bold;
    }
    .error-message {
        color: #dc3545;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)


class VoiceShoppingGUI:
    """Main GUI application class"""
    
    def __init__(self):
        """Initialize the GUI application"""
        self.initialize_session_state()
        self.product_search = self.get_product_search()
        self.cart_manager = self.get_cart_manager()
    
    def initialize_session_state(self):
        """Initialize Streamlit session state variables"""
        if 'session_id' not in st.session_state:
            st.session_state.session_id = f"gui-session-{int(time.time())}"
        
        if 'cart_items' not in st.session_state:
            st.session_state.cart_items = []
        
        if 'conversation_history' not in st.session_state:
            st.session_state.conversation_history = []
        
        if 'selected_products' not in st.session_state:
            st.session_state.selected_products = []
        
        if 'test_results' not in st.session_state:
            st.session_state.test_results = None
        
        if 'current_page' not in st.session_state:
            st.session_state.current_page = "🏠 Home"
        
        if 'voice_commands_processed' not in st.session_state:
            st.session_state.voice_commands_processed = 0
        
        if 'last_text_input' not in st.session_state:
            st.session_state.last_text_input = ""
    
    @st.cache_resource
    def get_product_search(_self):
        """Get cached product search instance"""
        return create_test_product_search()
    
    @st.cache_resource
    def get_cart_manager(_self):
        """Get cached cart manager instance"""
        return create_test_cart_manager()
    
    def run(self):
        """Main application entry point"""
        # Header
        st.markdown('<h1 class="main-header">🛒 Voice Shopping Assistant</h1>', 
                   unsafe_allow_html=True)
        
        # Sidebar navigation
        page = st.sidebar.selectbox(
            "Navigate to:",
            ["🏠 Home", "🛍️ Shop Products", "🛒 Shopping Cart", "💬 Chat Interface", 
             "🧪 Testing Tools", "📊 Analytics"],
            index=["🏠 Home", "🛍️ Shop Products", "🛒 Shopping Cart", "💬 Chat Interface", 
                   "🧪 Testing Tools", "📊 Analytics"].index(st.session_state.current_page)
        )
        
        # Update current page if changed
        if page != st.session_state.current_page:
            st.session_state.current_page = page
            st.rerun()
        
        # Display session info in sidebar
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"**Session ID:** `{st.session_state.session_id}`")
        st.sidebar.markdown(f"**Cart Items:** {len(st.session_state.cart_items)}")
        
        # Route to appropriate page
        if page == "🏠 Home":
            self.show_home_page()
        elif page == "🛍️ Shop Products":
            self.show_products_page()
        elif page == "🛒 Shopping Cart":
            self.show_cart_page()
        elif page == "💬 Chat Interface":
            self.show_chat_page()
        elif page == "🧪 Testing Tools":
            self.show_testing_page()
        elif page == "📊 Analytics":
            self.show_analytics_page()
    
    def show_home_page(self):
        """Display the home page"""
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 🎯 Quick Actions")
            if st.button("Browse Products", width="stretch"):
                st.session_state.current_page = "🛍️ Shop Products"
                st.rerun()
            if st.button("View Cart", width="stretch"):
                st.session_state.current_page = "🛒 Shopping Cart"
                st.rerun()
            if st.button("Start Shopping Chat", width="stretch"):
                st.session_state.current_page = "💬 Chat Interface"
                st.rerun()
        
        with col2:
            st.markdown("### 📊 System Status")
            catalog_stats = get_catalog_statistics()
            st.metric("Total Products", catalog_stats['total_products'])
            st.metric("Categories", len(catalog_stats['categories']))
            st.metric("In Stock", catalog_stats['in_stock_count'])
        
        with col3:
            st.markdown("### 🛒 Current Session")
            st.metric("Cart Items", len(st.session_state.cart_items))
            total_value = sum(item.get('price', 0) * item.get('quantity', 1) 
                            for item in st.session_state.cart_items)
            st.metric("Cart Value", f"${total_value:.2f}")
        
        # Recent activity
        st.markdown("### 📝 Recent Activity")
        if st.session_state.conversation_history:
            for i, msg in enumerate(st.session_state.conversation_history[-5:]):
                with st.expander(f"Message {len(st.session_state.conversation_history) - 4 + i}"):
                    st.write(f"**You:** {msg.get('user', 'N/A')}")
                    st.write(f"**Assistant:** {msg.get('assistant', 'N/A')}")
        else:
            st.info("No recent activity. Start shopping to see your conversation history!")
        
        # Product categories overview
        st.markdown("### 🏷️ Product Categories")
        catalog_stats = get_catalog_statistics()
        categories_df = pd.DataFrame(
            list(catalog_stats['categories'].items()),
            columns=['Category', 'Count']
        )
        
        fig = px.bar(categories_df, x='Category', y='Count', 
                    title="Products by Category")
        st.plotly_chart(fig, width="stretch")
    
    def show_products_page(self):
        """Display the products browsing page"""
        st.markdown("## 🛍️ Browse Products")
        
        # Search and filter controls
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search_query = st.text_input("🔍 Search products", 
                                       placeholder="Enter product name, brand, or description...")
        
        with col2:
            categories = ["All"] + list(set(p.category for p in get_sample_products()))
            selected_category = st.selectbox("Category", categories)
        
        with col3:
            price_range = st.slider("Price Range", 0, 1500, (0, 1500), step=50)
        
        # Advanced filters in expander
        with st.expander("🔧 Advanced Filters"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                brands = ["All"] + list(set(p.brand for p in get_sample_products()))
                selected_brand = st.selectbox("Brand", brands)
            
            with col2:
                materials = ["All"] + list(set(p.material for p in get_sample_products()))
                selected_material = st.selectbox("Material", materials)
            
            with col3:
                stock_filter = st.selectbox("Stock Status", ["All", "In Stock", "Out of Stock"])
        
        # Apply filters
        products = self.filter_products(
            search_query, selected_category, price_range, 
            selected_brand, selected_material, stock_filter
        )
        
        # Display results
        st.markdown(f"### Found {len(products)} products")
        
        # Product grid
        cols_per_row = 3
        for i in range(0, len(products), cols_per_row):
            cols = st.columns(cols_per_row)
            
            for j, col in enumerate(cols):
                if i + j < len(products):
                    product = products[i + j]
                    self.display_product_card(product, col)
    
    def filter_products(self, query: str, category: str, price_range: tuple,
                       brand: str, material: str, stock_filter: str) -> List[Product]:
        """Filter products based on search criteria"""
        products = get_sample_products()
        
        # Text search
        if query:
            products = self.product_search.fuzzy_search(query, limit=50)
        
        # Category filter
        if category != "All":
            products = [p for p in products if p.category.lower() == category.lower()]
        
        # Price filter
        products = [p for p in products if price_range[0] <= p.price <= price_range[1]]
        
        # Brand filter
        if brand != "All":
            products = [p for p in products if p.brand.lower() == brand.lower()]
        
        # Material filter
        if material != "All":
            products = [p for p in products if p.material.lower() == material.lower()]
        
        # Stock filter
        if stock_filter == "In Stock":
            products = [p for p in products if p.in_stock]
        elif stock_filter == "Out of Stock":
            products = [p for p in products if not p.in_stock]
        
        return products
    
    def display_product_card(self, product: Product, container):
        """Display a product card in the given container"""
        with container:
            with st.container():
                st.markdown(f"**{product.name}**")
                st.markdown(f"*{product.brand}* • {product.category}")
                st.markdown(f"**${product.price:.2f}**")
                
                # Stock status
                if product.in_stock:
                    st.markdown('<span class="success-message">✅ In Stock</span>', 
                              unsafe_allow_html=True)
                else:
                    st.markdown('<span class="error-message">❌ Out of Stock</span>', 
                              unsafe_allow_html=True)
                
                # Product details
                with st.expander("Details"):
                    st.write(f"**Material:** {product.material}")
                    st.write(f"**Colors:** {', '.join(product.available_colors)}")
                    st.write(f"**Sizes:** {', '.join(product.available_sizes)}")
                    if product.description:
                        st.write(f"**Description:** {product.description}")
                
                # Add to cart controls
                if product.in_stock:
                    col1, col2 = st.columns(2)
                    with col1:
                        quantity = st.number_input(
                            "Qty", min_value=1, max_value=10, value=1, 
                            key=f"qty_{product.id}"
                        )
                    with col2:
                        if st.button("Add to Cart", key=f"add_{product.id}"):
                            self.add_to_cart(product, quantity)
                            st.success("Added to cart!")
                            time.sleep(1)
                            st.rerun()
    
    def add_to_cart(self, product: Product, quantity: int):
        """Add product to cart"""
        cart_item = {
            'product_id': product.id,
            'name': product.name,
            'price': product.price,
            'quantity': quantity,
            'brand': product.brand,
            'category': product.category
        }
        
        # Check if item already exists
        existing_item = None
        for item in st.session_state.cart_items:
            if item['product_id'] == product.id:
                existing_item = item
                break
        
        if existing_item:
            existing_item['quantity'] += quantity
        else:
            st.session_state.cart_items.append(cart_item)
    
    def show_cart_page(self):
        """Display the shopping cart page"""
        st.markdown("## 🛒 Shopping Cart")
        
        if not st.session_state.cart_items:
            st.info("Your cart is empty. Browse products to add items!")
            if st.button("Browse Products"):
                st.session_state.current_page = "🛍️ Shop Products"
                st.rerun()
            return
        
        # Cart summary
        total_items = sum(item['quantity'] for item in st.session_state.cart_items)
        total_value = sum(item['price'] * item['quantity'] for item in st.session_state.cart_items)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Items", total_items)
        with col2:
            st.metric("Total Value", f"${total_value:.2f}")
        with col3:
            if st.button("Clear Cart", type="secondary"):
                st.session_state.cart_items = []
                st.rerun()
        
        st.markdown("---")
        
        # Cart items
        for i, item in enumerate(st.session_state.cart_items):
            col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
            
            with col1:
                st.markdown(f"**{item['name']}**")
                st.markdown(f"*{item['brand']}* • {item['category']}")
            
            with col2:
                st.markdown(f"${item['price']:.2f}")
            
            with col3:
                new_qty = st.number_input(
                    "Quantity", min_value=1, max_value=10, 
                    value=item['quantity'], key=f"cart_qty_{i}"
                )
                if new_qty != item['quantity']:
                    item['quantity'] = new_qty
                    st.rerun()
            
            with col4:
                st.markdown(f"${item['price'] * item['quantity']:.2f}")
            
            with col5:
                if st.button("Remove", key=f"remove_{i}"):
                    st.session_state.cart_items.pop(i)
                    st.rerun()
            
            st.markdown("---")
        
        # Checkout section
        st.markdown("### 💳 Checkout")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Total: ${total_value:.2f}**")
        
        with col2:
            if st.button("Proceed to Checkout", type="primary"):
                st.success("🎉 Order placed successfully!")
                st.balloons()
                st.session_state.cart_items = []
                time.sleep(2)
                st.rerun()
    
    def show_chat_page(self):
        """Display the chat interface page"""
        st.markdown("## 💬 Voice Shopping Chat")
        
        # Add speech-to-text functionality
        self._add_speech_to_text_component()
        
        # Chat input with voice support
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_input = st.text_input(
                "Type or speak your shopping request:",
                placeholder="e.g., 'Add two red shirts to my cart' or 'Show me blue jeans under $100'",
                key="chat_input"
            )
        
        with col2:
            st.markdown("🎤 **Voice Input**")
            # Voice input will be handled by JavaScript
        
        # Control buttons
        col1, col2, col3 = st.columns([1, 1, 3])
        
        with col1:
            if st.button("Send", type="primary"):
                if user_input:
                    # Check if this might be a voice command (contains common voice patterns)
                    is_voice = any(phrase in user_input.lower() for phrase in [
                        'add', 'remove', 'show me', 'search for', 'find', 'help'
                    ])
                    self.process_chat_message(user_input, is_voice_command=is_voice)
                    st.rerun()
        
        with col2:
            if st.button("Clear History"):
                st.session_state.conversation_history = []
                st.rerun()
        
        # Hidden input for voice command processing
        voice_command = st.text_input("Voice Command Trigger", key="voice_command_trigger", 
                                     label_visibility="collapsed", 
                                     help="This field is used for voice command processing")
        
        # Process voice command if detected
        if voice_command and voice_command != st.session_state.get('last_voice_command', ''):
            st.session_state.last_voice_command = voice_command
            # Extract the actual command (remove timestamp)
            actual_command = voice_command.split('_')[0] if '_' in voice_command else voice_command
            if actual_command.strip():
                self.process_chat_message(actual_command, is_voice_command=True)
                st.rerun()
        
        # Alternative: Check if text input changed significantly (possible voice input)
        if user_input and user_input != st.session_state.last_text_input:
            # Check if this looks like a voice command that appeared suddenly
            if (len(user_input) > 10 and  # Reasonable length
                any(word in user_input.lower() for word in ['add', 'show', 'search', 'find', 'remove', 'help']) and
                st.session_state.last_text_input == ""):  # Was empty before
                
                # Auto-process if it looks like voice input
                st.session_state.last_text_input = user_input
                self.process_chat_message(user_input, is_voice_command=True)
                st.rerun()
            else:
                st.session_state.last_text_input = user_input
        
        with col3:
            if st.session_state.voice_commands_processed > 0:
                st.success(f"🎤 {st.session_state.voice_commands_processed} voice commands processed!")
            else:
                st.markdown("*Click 🎤 Start Voice to speak your request*")
        
        # Chat history
        st.markdown("### 📝 Conversation History")
        
        if st.session_state.conversation_history:
            for i, msg in enumerate(reversed(st.session_state.conversation_history)):
                with st.container():
                    st.markdown(f"**You:** {msg['user']}")
                    st.markdown(f"**Assistant:** {msg['assistant']}")
                    st.markdown("---")
        else:
            st.info("Start a conversation by typing a shopping request above!")
        
        # Quick actions
        st.markdown("### ⚡ Quick Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Show my cart"):
                self.process_chat_message("show me my cart")
                st.rerun()
        
        with col2:
            if st.button("Search for shirts"):
                self.process_chat_message("search for shirts")
                st.rerun()
        
        with col3:
            if st.button("Help me shop"):
                self.process_chat_message("help me with shopping")
                st.rerun()
    
    def process_chat_message(self, user_input: str, is_voice_command: bool = False):
        """Process a chat message and generate response"""
        # Process the command and update cart if needed
        response = self.process_shopping_command(user_input)
        
        # Track voice commands
        if is_voice_command:
            st.session_state.voice_commands_processed += 1
        
        # Add to conversation history
        st.session_state.conversation_history.append({
            'user': user_input,
            'assistant': response,
            'timestamp': datetime.now().isoformat(),
            'is_voice': is_voice_command
        })
    
    def process_shopping_command(self, user_input: str) -> str:
        """Process a shopping command and update cart accordingly"""
        user_input_lower = user_input.lower()
        
        # ADD commands
        if any(word in user_input_lower for word in ['add', 'put', 'include']):
            return self.handle_add_command(user_input_lower)
        
        # REMOVE commands
        elif any(word in user_input_lower for word in ['remove', 'delete', 'take out']):
            return self.handle_remove_command(user_input_lower)
        
        # SEARCH/SHOW commands
        elif any(word in user_input_lower for word in ['search', 'find', 'look for', 'show']):
            if 'cart' in user_input_lower:
                return self.handle_show_cart_command()
            else:
                return self.handle_search_command(user_input_lower)
        
        # HELP commands
        elif any(word in user_input_lower for word in ['help', 'assist']):
            return self.handle_help_command()
        
        # CLEAR cart commands
        elif any(word in user_input_lower for word in ['clear', 'empty']):
            if 'cart' in user_input_lower:
                return self.handle_clear_cart_command()
        
        else:
            return "I understand you want to shop! You can ask me to add items, search for products, or check your cart. What would you like to do?"
    
    def handle_add_command(self, user_input: str) -> str:
        """Handle add item commands"""
        # Extract product information from the command
        products = get_sample_products()
        
        # Simple product matching based on keywords
        found_products = []
        
        # Check for specific product types (order matters - more specific first)
        product_keywords = {
            'smartphone': ['smartphone'],  # More specific first
            'headphones': ['headphones', 'earphones'],
            'laptop': ['laptop'],
            'computer': ['computer'],
            'phone': ['phone'],  # Less specific, comes after smartphone
            'shirt': ['shirt', 'tshirt', 't-shirt'],
            'jeans': ['jeans'],
            'pants': ['pants', 'trousers'],
            'shoes': ['shoes', 'sneakers', 'boots'],
            'dress': ['dress'],
            'jacket': ['jacket', 'coat']
        }
        
        # Find the best matching product type (most specific match first)
        best_match = None
        best_score = 0
        
        for product_type, keywords in product_keywords.items():
            for keyword in keywords:
                if keyword in user_input:
                    # Prefer exact matches and longer keywords
                    score = len(keyword) + (10 if user_input.count(keyword) == 1 else 0)
                    if score > best_score:
                        best_score = score
                        best_match = product_type
        
        if best_match:
            # Find matching products for the best match only
            keywords = product_keywords[best_match]
            matching_products = [p for p in products if any(kw in p.name.lower() for kw in keywords)]
            if matching_products:
                found_products.extend(matching_products[:1])  # Only add 1 product
        
        # If no specific products found, try general search
        if not found_products:
            # Look for any product name mentioned
            for product in products:
                if any(word in user_input for word in product.name.lower().split()):
                    found_products.append(product)
                    break
        
        # If still no products found, add a default shirt
        if not found_products:
            default_products = [p for p in products if 'shirt' in p.name.lower()]
            if default_products:
                found_products = [default_products[0]]
        
        # Extract quantity
        quantity = 1
        quantity_words = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5}
        for word, num in quantity_words.items():
            if word in user_input:
                quantity = num
                break
        
        # Check for numbers
        import re
        numbers = re.findall(r'\d+', user_input)
        if numbers:
            try:
                quantity = int(numbers[0])
            except ValueError:
                pass
        
        # Extract color preference
        color = None
        colors = ['red', 'blue', 'green', 'white', 'black', 'yellow', 'pink', 'purple', 'orange', 'gray', 'grey']
        for c in colors:
            if c in user_input:
                color = c
                break
        
        # Add products to cart
        added_items = []
        for product in found_products:
            if product.in_stock:
                # Filter by color if specified and available
                if color and color not in [c.lower() for c in product.available_colors]:
                    continue
                
                self.add_to_cart(product, quantity)
                color_text = f" in {color}" if color else ""
                added_items.append(f"{quantity} {product.name}{color_text}")
        
        if added_items:
            items_text = ", ".join(added_items)
            return f"✅ Added {items_text} to your cart! You now have {len(st.session_state.cart_items)} items."
        else:
            return "❌ Sorry, I couldn't find that item in stock. Try browsing our products or ask for something else!"
    
    def handle_remove_command(self, user_input: str) -> str:
        """Handle remove item commands"""
        if not st.session_state.cart_items:
            return "Your cart is empty, so there's nothing to remove."
        
        # Handle remove all
        if 'all' in user_input or 'everything' in user_input:
            count = len(st.session_state.cart_items)
            st.session_state.cart_items.clear()
            return f"✅ Removed all {count} items from your cart."
        
        # Extract what to remove
        user_input_lower = user_input.lower()
        
        # Define product keywords for removal
        product_keywords = {
            'shirt': ['shirt', 't-shirt', 'tshirt'],
            'jeans': ['jeans', 'jean'],
            'pants': ['pants', 'trousers'],
            'shoes': ['shoes', 'sneakers', 'boots'],
            'headphones': ['headphones', 'earphones'],
            'phone': ['phone', 'smartphone'],
            'laptop': ['laptop', 'computer'],
            'dress': ['dress'],
            'jacket': ['jacket', 'coat']
        }
        
        # Find what product type to remove
        product_to_remove = None
        for product_type, keywords in product_keywords.items():
            if any(keyword in user_input_lower for keyword in keywords):
                product_to_remove = product_type
                break
        
        # Extract quantity to remove
        quantity_to_remove = 1  # Default
        quantity_words = {'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5}
        for word, num in quantity_words.items():
            if word in user_input_lower:
                quantity_to_remove = num
                break
        
        # Check for numbers
        import re
        numbers = re.findall(r'\d+', user_input_lower)
        if numbers:
            try:
                quantity_to_remove = int(numbers[0])
            except ValueError:
                pass
        
        # Find and remove matching items
        if product_to_remove:
            keywords = product_keywords[product_to_remove]
            removed_items = []
            items_to_remove = []
            
            # Find items that match the product type
            for i, item in enumerate(st.session_state.cart_items):
                if any(keyword in item['name'].lower() for keyword in keywords):
                    items_to_remove.append((i, item))
            
            if not items_to_remove:
                return f"❌ I couldn't find any {product_to_remove} in your cart."
            
            # Remove the specified quantity
            removed_count = 0
            for i, item in reversed(items_to_remove):  # Reverse to maintain indices
                if removed_count >= quantity_to_remove:
                    break
                
                if item['quantity'] > 1 and quantity_to_remove == 1:
                    # Reduce quantity by 1
                    item['quantity'] -= 1
                    removed_items.append(f"1 {item['name']}")
                    removed_count += 1
                else:
                    # Remove entire item
                    removed_item = st.session_state.cart_items.pop(i)
                    removed_items.append(f"{removed_item['quantity']} {removed_item['name']}")
                    removed_count += removed_item['quantity']
            
            if removed_items:
                items_text = ", ".join(removed_items)
                return f"✅ Removed {items_text} from your cart. You now have {len(st.session_state.cart_items)} items."
            else:
                return f"❌ Couldn't remove {quantity_to_remove} {product_to_remove} from your cart."
        
        # Fallback: if no specific product mentioned, remove last item
        elif 'last' in user_input_lower or 'recent' in user_input_lower:
            removed_item = st.session_state.cart_items.pop()
            return f"✅ Removed {removed_item['name']} from your cart. You now have {len(st.session_state.cart_items)} items."
        
        else:
            # If no specific item mentioned, ask for clarification
            if len(st.session_state.cart_items) == 1:
                # Only one item, remove it
                removed_item = st.session_state.cart_items.pop()
                return f"✅ Removed {removed_item['name']} from your cart. Your cart is now empty."
            else:
                # Multiple items, ask for clarification
                items_list = [f"{item['quantity']}x {item['name']}" for item in st.session_state.cart_items]
                items_text = ", ".join(items_list)
                return f"❓ Which item would you like me to remove? Your cart has: {items_text}. Please specify which item to remove."
    
    def handle_show_cart_command(self) -> str:
        """Handle show cart commands"""
        if not st.session_state.cart_items:
            return "🛒 Your cart is empty. Start shopping by asking me to add some items!"
        
        cart_summary = []
        total_value = 0
        
        for item in st.session_state.cart_items:
            item_total = item['price'] * item['quantity']
            total_value += item_total
            cart_summary.append(f"• {item['quantity']}x {item['name']} - ${item_total:.2f}")
        
        summary_text = "\n".join(cart_summary)
        return f"🛒 **Your Cart ({len(st.session_state.cart_items)} items):**\n{summary_text}\n\n**Total: ${total_value:.2f}**"
    
    def handle_search_command(self, user_input: str) -> str:
        """Handle search commands"""
        # Extract search terms more carefully
        search_terms = user_input.lower()
        
        # Remove common command words
        for phrase in ['search for', 'find me', 'look for', 'show me', 'i want', 'get me']:
            search_terms = search_terms.replace(phrase, '')
        
        # Extract price constraint if mentioned
        price_limit = None
        import re
        price_matches = re.findall(r'under\s+\$?(\d+)', search_terms)
        if price_matches:
            price_limit = float(price_matches[0])
            search_terms = re.sub(r'under\s+\$?\d+', '', search_terms)
        
        # Clean up search terms
        search_terms = search_terms.strip()
        
        if not search_terms:
            return "What would you like me to search for? Try asking for shirts, jeans, electronics, or any other product!"
        
        # Use more targeted search with filters
        filters = {}
        if price_limit:
            filters['price_max'] = price_limit
        
        # Try exact product search first
        products = []
        all_products = get_sample_products()
        
        # Define product categories for better matching
        product_categories = {
            'jeans': ['jeans', 'jean'],
            'shirt': ['shirt', 't-shirt', 'tshirt'],
            'shoes': ['shoes', 'sneakers', 'boots'],
            'headphones': ['headphones', 'earphones'],
            'phone': ['phone', 'smartphone'],
            'laptop': ['laptop', 'computer'],
            'dress': ['dress'],
            'pants': ['pants', 'trousers'],
            'jacket': ['jacket', 'coat']
        }
        
        # First, try to identify the main product type from search terms
        main_product_type = None
        for category, keywords in product_categories.items():
            if any(keyword in search_terms for keyword in keywords):
                main_product_type = category
                break
        
        # Look for products matching the specific type
        if main_product_type:
            category_keywords = product_categories[main_product_type]
            for product in all_products:
                # Check if product matches the category
                if any(keyword in product.name.lower() for keyword in category_keywords):
                    # Also check for color/attribute matches if specified
                    search_words = search_terms.split()
                    color_match = True
                    
                    # If color is specified, make sure product has that color
                    colors = ['red', 'blue', 'green', 'white', 'black', 'yellow', 'pink', 'purple', 'orange', 'gray', 'grey']
                    specified_colors = [word for word in search_words if word in colors]
                    
                    if specified_colors:
                        # Check if product has the specified color
                        color_match = any(color in product.available_colors or color in product.name.lower() 
                                        for color in specified_colors)
                    
                    if color_match and (not price_limit or product.price <= price_limit):
                        products.append(product)
        else:
            # Fallback: look for any matches in product names
            for product in all_products:
                if any(term in product.name.lower() for term in search_terms.split()):
                    if not price_limit or product.price <= price_limit:
                        products.append(product)
        
        # If no exact matches, use fuzzy search
        if not products:
            if price_limit:
                # Filter by price first, then search
                filtered_products = [p for p in all_products if p.price <= price_limit]
                # Create temporary search instance with filtered products
                temp_search = ProductSearch(filtered_products)
                products = temp_search.fuzzy_search(search_terms, limit=5)
            else:
                products = self.product_search.fuzzy_search(search_terms, limit=5)
        
        # Limit results
        products = products[:5]
        
        if products:
            results = []
            for product in products:
                stock_status = "✅ In Stock" if product.in_stock else "❌ Out of Stock"
                results.append(f"• {product.name} ({product.brand}) - ${product.price:.2f} {stock_status}")
            
            results_text = "\n".join(results)
            price_text = f" under ${price_limit}" if price_limit else ""
            return f"🔍 **Found {len(products)} products for '{search_terms}'{price_text}:**\n{results_text}\n\nYou can ask me to add any of these to your cart!"
        else:
            price_text = f" under ${price_limit}" if price_limit else ""
            return f"❌ Sorry, I couldn't find any products matching '{search_terms}'{price_text}'. Try searching for shirts, electronics, or other categories!"
    
    def handle_help_command(self) -> str:
        """Handle help commands"""
        return """🤖 **I can help you shop! Here's what you can ask me:**

**Adding Items:**
• "Add a red shirt to my cart"
• "Put two blue jeans in my cart"
• "I want some headphones"

**Managing Cart:**
• "Show me my cart"
• "Remove the last item"
• "Clear my cart"

**Searching:**
• "Search for laptops under $1000"
• "Find me some running shoes"
• "Show me electronics"

Just tell me what you want and I'll help you find it! 🛍️"""
    
    def handle_clear_cart_command(self) -> str:
        """Handle clear cart commands"""
        if not st.session_state.cart_items:
            return "Your cart is already empty!"
        
        count = len(st.session_state.cart_items)
        st.session_state.cart_items.clear()
        return f"✅ Cleared your cart! Removed {count} items."
    
    def show_testing_page(self):
        """Display the testing tools page"""
        st.markdown("## 🧪 Testing Tools")
        
        # Test runner section
        st.markdown("### 🚀 End-to-End Tests")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Run All Tests", type="primary"):
                with st.spinner("Running comprehensive tests..."):
                    try:
                        # Run tests and capture results
                        runner = EndToEndTestRunner()
                        report = runner.run_all_tests()
                        st.session_state.test_results = report
                        
                        # Display results
                        summary = report['test_summary']
                        if summary['scenario_success_rate'] >= 0.8:
                            st.success(f"✅ Tests passed! Success rate: {summary['scenario_success_rate']:.1%}")
                        else:
                            st.error(f"❌ Tests failed! Success rate: {summary['scenario_success_rate']:.1%}")
                        
                    except Exception as e:
                        st.error(f"Test execution failed: {str(e)}")
        
        with col2:
            if st.button("Run Single Scenario"):
                scenario = ScenarioBuilder.create_basic_shopping_scenario()
                with st.spinner("Running basic shopping scenario..."):
                    try:
                        runner = EndToEndTestRunner()
                        result = runner.run_custom_scenario(scenario)
                        
                        metrics = result.calculate_metrics()
                        st.info(f"Scenario completed with {metrics['success_rate']:.1%} success rate")
                        
                    except Exception as e:
                        st.error(f"Scenario execution failed: {str(e)}")
        
        # Test results display
        if st.session_state.test_results:
            st.markdown("### 📊 Latest Test Results")
            
            summary = st.session_state.test_results['test_summary']
            
            # Metrics display
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Scenarios", f"{summary['successful_scenarios']}/{summary['total_scenarios']}")
            
            with col2:
                st.metric("Commands", f"{summary['successful_commands']}/{summary['total_commands']}")
            
            with col3:
                st.metric("Success Rate", f"{summary['scenario_success_rate']:.1%}")
            
            with col4:
                st.metric("Avg Processing Time", f"{summary['avg_processing_time']:.3f}s")
            
            # Detailed results
            with st.expander("Detailed Results"):
                st.json(st.session_state.test_results)
        
        # Manual testing section
        st.markdown("### 🔧 Manual Testing")
        
        test_command = st.text_input(
            "Test Command:",
            placeholder="Enter a voice command to test..."
        )
        
        if st.button("Test Command") and test_command:
            with st.spinner("Processing command..."):
                response = self.generate_mock_response(test_command)
                st.success(f"Response: {response}")
        
        # System status
        st.markdown("### 🔍 System Status")
        
        catalog_stats = get_catalog_statistics()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Product Catalog:**")
            st.write(f"- Total Products: {catalog_stats['total_products']}")
            st.write(f"- Categories: {len(catalog_stats['categories'])}")
            st.write(f"- In Stock: {catalog_stats['in_stock_count']}")
        
        with col2:
            st.markdown("**Session Info:**")
            st.write(f"- Session ID: {st.session_state.session_id}")
            st.write(f"- Cart Items: {len(st.session_state.cart_items)}")
            st.write(f"- Conversation History: {len(st.session_state.conversation_history)}")
    
    def show_analytics_page(self):
        """Display analytics and insights page"""
        st.markdown("## 📊 Analytics & Insights")
        
        # Product catalog analytics
        st.markdown("### 📦 Product Catalog Analysis")
        
        products = get_sample_products()
        catalog_stats = get_catalog_statistics()
        
        # Category distribution
        col1, col2 = st.columns(2)
        
        with col1:
            categories_df = pd.DataFrame(
                list(catalog_stats['categories'].items()),
                columns=['Category', 'Count']
            )
            
            fig = px.pie(categories_df, values='Count', names='Category', 
                        title="Products by Category")
            st.plotly_chart(fig, width="stretch")
        
        with col2:
            # Price distribution
            prices = [p.price for p in products]
            fig = px.histogram(x=prices, nbins=20, title="Price Distribution")
            fig.update_xaxis(title="Price ($)")
            fig.update_yaxis(title="Number of Products")
            st.plotly_chart(fig, width="stretch")
        
        # Brand analysis
        st.markdown("### 🏷️ Brand Analysis")
        
        brand_counts = {}
        for product in products:
            brand_counts[product.brand] = brand_counts.get(product.brand, 0) + 1
        
        brands_df = pd.DataFrame(
            list(brand_counts.items()),
            columns=['Brand', 'Product Count']
        ).sort_values('Product Count', ascending=False)
        
        fig = px.bar(brands_df.head(10), x='Brand', y='Product Count', 
                    title="Top 10 Brands by Product Count")
        st.plotly_chart(fig, width="stretch")
        
        # Stock analysis
        st.markdown("### 📈 Stock Analysis")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("In Stock", catalog_stats['in_stock_count'])
        
        with col2:
            st.metric("Out of Stock", catalog_stats['out_of_stock_count'])
        
        with col3:
            stock_rate = catalog_stats['in_stock_count'] / catalog_stats['total_products']
            st.metric("Stock Rate", f"{stock_rate:.1%}")
        
        # Session analytics
        if st.session_state.conversation_history or st.session_state.cart_items:
            st.markdown("### 🛒 Session Analytics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Cart Summary:**")
                if st.session_state.cart_items:
                    cart_df = pd.DataFrame(st.session_state.cart_items)
                    st.dataframe(cart_df[['name', 'brand', 'quantity', 'price']], 
                               width="stretch")
                else:
                    st.info("No items in cart")
            
            with col2:
                st.markdown("**Conversation Activity:**")
                if st.session_state.conversation_history:
                    st.write(f"Total Messages: {len(st.session_state.conversation_history)}")
                    
                    # Message timeline
                    if len(st.session_state.conversation_history) > 1:
                        timestamps = [msg.get('timestamp', '') for msg in st.session_state.conversation_history]
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            y=list(range(len(timestamps))),
                            x=timestamps,
                            mode='markers+lines',
                            name='Messages'
                        ))
                        fig.update_layout(title="Message Timeline", 
                                        xaxis_title="Time", yaxis_title="Message #")
                        st.plotly_chart(fig, width="stretch")
                else:
                    st.info("No conversation history")
    
    def _add_speech_to_text_component(self):
        """Add speech-to-text functionality using Web Speech API"""
        
        # Add the speech-to-text HTML/JavaScript component
        speech_component = """
        <div style="background-color: #f0f2f6; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <div style="display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;">
                <button id="startVoice" onclick="startVoiceRecognition()" 
                        style="background-color: #1f77b4; color: white; border: none; padding: 0.5rem 1rem; 
                               border-radius: 4px; cursor: pointer; font-size: 14px;">
                    🎤 Start Voice
                </button>
                <button id="stopVoice" onclick="stopVoiceRecognition()" 
                        style="background-color: #dc3545; color: white; border: none; padding: 0.5rem 1rem; 
                               border-radius: 4px; cursor: pointer; font-size: 14px;" disabled>
                    ⏹️ Stop Voice
                </button>
                <span id="voiceStatus" style="font-weight: bold; color: #666;">Ready to listen</span>
            </div>
            <div id="voiceResult" style="margin-top: 0.5rem; padding: 0.5rem; background-color: white; 
                                        border-radius: 4px; min-height: 2rem; border: 1px solid #ddd;">
                <em>Voice input will appear here...</em>
            </div>
        </div>

        <script>
        let recognition = null;
        let isListening = false;

        // Check if browser supports speech recognition
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            
            // Configure recognition
            recognition.continuous = false;
            recognition.interimResults = true;
            recognition.lang = 'en-US';
            
            // Event handlers
            recognition.onstart = function() {
                isListening = true;
                document.getElementById('voiceStatus').textContent = '🎤 Listening...';
                document.getElementById('voiceStatus').style.color = '#28a745';
                document.getElementById('startVoice').disabled = true;
                document.getElementById('stopVoice').disabled = false;
                document.getElementById('voiceResult').innerHTML = '<em>Listening for your voice...</em>';
            };
            
            recognition.onresult = function(event) {
                let transcript = '';
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    transcript += event.results[i][0].transcript;
                }
                
                // Update the voice result display
                document.getElementById('voiceResult').textContent = transcript;
                
                // If final result, update the text input and auto-submit
                if (event.results[event.results.length - 1].isFinal) {
                    // Find the Streamlit text input and update it
                    const textInputs = document.querySelectorAll('input[type="text"]');
                    let chatInput = null;
                    
                    // Find the chat input specifically
                    for (let input of textInputs) {
                        if (input.placeholder && input.placeholder.includes('shopping request')) {
                            chatInput = input;
                            break;
                        }
                    }
                    
                    if (chatInput && transcript.trim()) {
                        chatInput.value = transcript;
                        chatInput.dispatchEvent(new Event('input', { bubbles: true }));
                        chatInput.dispatchEvent(new Event('change', { bubbles: true }));
                        
                        // Focus on the input
                        chatInput.focus();
                        
                        // Auto-submit by updating the hidden voice command trigger
                        setTimeout(function() {
                            // Try multiple methods to find the voice trigger input
                            let voiceTrigger = null;
                            
                            // Method 1: Look for input with specific help text
                            const inputs = document.querySelectorAll('input[type="text"]');
                            for (let input of inputs) {
                                if (input.title && input.title.includes('voice command processing')) {
                                    voiceTrigger = input;
                                    break;
                                }
                            }
                            
                            // Method 2: Look for collapsed label input
                            if (!voiceTrigger) {
                                const labels = document.querySelectorAll('label');
                                for (let label of labels) {
                                    if (label.textContent.includes('Voice Command Trigger')) {
                                        const inputId = label.getAttribute('for');
                                        if (inputId) {
                                            voiceTrigger = document.getElementById(inputId);
                                            break;
                                        }
                                    }
                                }
                            }
                            
                            // Method 3: Fallback - find by data attribute or class
                            if (!voiceTrigger) {
                                voiceTrigger = document.querySelector('[data-testid*="voice"]') || 
                                             document.querySelector('input[aria-label*="Voice"]');
                            }
                            
                            if (voiceTrigger) {
                                voiceTrigger.value = transcript + '_' + Date.now(); // Add timestamp to ensure uniqueness
                                voiceTrigger.dispatchEvent(new Event('input', { bubbles: true }));
                                voiceTrigger.dispatchEvent(new Event('change', { bubbles: true }));
                                
                                document.getElementById('voiceStatus').textContent = '🚀 Processing voice command...';
                                document.getElementById('voiceStatus').style.color = '#1f77b4';
                                
                                console.log('Voice command triggered:', transcript);
                            } else {
                                // Fallback method: Try alternative approach
                                console.log('Trying fallback method for voice command:', transcript);
                                if (triggerVoiceCommand(transcript)) {
                                    document.getElementById('voiceStatus').textContent = '🚀 Processing voice command (fallback)...';
                                    document.getElementById('voiceStatus').style.color = '#1f77b4';
                                } else {
                                    console.error('All voice trigger methods failed');
                                    document.getElementById('voiceStatus').textContent = '❌ Auto-processing failed - please click Send';
                                    document.getElementById('voiceStatus').style.color = '#dc3545';
                                }
                            }
                        }, 500); // 500ms delay to ensure input is processed
                    }
                }
            };
            
            recognition.onerror = function(event) {
                console.error('Speech recognition error:', event.error);
                let errorMsg = 'Error: ' + event.error;
                if (event.error === 'not-allowed') {
                    errorMsg = 'Microphone access denied. Please allow microphone access.';
                } else if (event.error === 'no-speech') {
                    errorMsg = 'No speech detected. Please try again.';
                }
                document.getElementById('voiceStatus').textContent = '❌ ' + errorMsg;
                document.getElementById('voiceStatus').style.color = '#dc3545';
                resetVoiceButtons();
            };
            
            recognition.onend = function() {
                isListening = false;
                if (document.getElementById('voiceStatus').textContent.includes('Listening')) {
                    document.getElementById('voiceStatus').textContent = '✅ Voice input complete';
                    document.getElementById('voiceStatus').style.color = '#28a745';
                }
                resetVoiceButtons();
            };
            
        } else {
            // Browser doesn't support speech recognition
            document.getElementById('startVoice').disabled = true;
            document.getElementById('stopVoice').disabled = true;
            document.getElementById('voiceStatus').textContent = '❌ Speech recognition not supported';
            document.getElementById('voiceStatus').style.color = '#dc3545';
            document.getElementById('voiceResult').innerHTML = '<em>Your browser does not support speech recognition. Please use Chrome, Edge, or Safari.</em>';
        }

        function startVoiceRecognition() {
            if (recognition && !isListening) {
                recognition.start();
            }
        }

        function stopVoiceRecognition() {
            if (recognition && isListening) {
                recognition.stop();
            }
        }

        function resetVoiceButtons() {
            document.getElementById('startVoice').disabled = false;
            document.getElementById('stopVoice').disabled = true;
        }
        
        // Alternative method: Use Streamlit's component communication
        function triggerVoiceCommand(transcript) {
            // Try to trigger Streamlit rerun by modifying a visible element
            const chatInput = document.querySelector('input[placeholder*="shopping request"]');
            if (chatInput) {
                chatInput.value = transcript;
                chatInput.dispatchEvent(new Event('input', { bubbles: true }));
                chatInput.dispatchEvent(new Event('change', { bubbles: true }));
                
                // Simulate Enter key press to trigger form submission
                const enterEvent = new KeyboardEvent('keydown', {
                    key: 'Enter',
                    code: 'Enter',
                    keyCode: 13,
                    which: 13,
                    bubbles: true
                });
                chatInput.dispatchEvent(enterEvent);
                
                return true;
            }
            return false;
        }
        </script>
        """
        
        # Display the component
        st.components.v1.html(speech_component, height=120)
        
        # Add instructions
        st.markdown("""
        **🎤 Voice Instructions:**
        - Click "🎤 Start Voice" to begin speaking
        - Speak clearly: *"Add two red shirts to my cart"*
        - Your speech will appear in the text box below
        - **Command will be processed automatically!** ✨
        - Works best in Chrome, Edge, and Safari browsers
        
        **Example Voice Commands:**
        - *"Add a blue shirt to my cart"*
        - *"Show me red jeans under 100 dollars"*
        - *"Remove the last item from cart"*
        - *"What's in my cart?"*
        """)


def main():
    """Main application entry point"""
    app = VoiceShoppingGUI()
    app.run()


if __name__ == "__main__":
    main()