# Voice Shopping Assistant GUI

A modern web-based interface for the Voice Shopping Assistant built with Streamlit.

## Features

### 🏠 Home Dashboard
- Quick action buttons for common tasks
- System status and metrics
- Cart summary and recent activity
- Product category overview with interactive charts

### 🛍️ Product Browsing
- **Search & Filter**: Text search with category, price, brand, and material filters
- **Product Cards**: Detailed product information with images, descriptions, and availability
- **Add to Cart**: Direct add-to-cart functionality with quantity and variant selection
- **Advanced Filters**: Expandable filter panel for refined searching

### 🛒 Shopping Cart
- **Cart Management**: View, modify, and remove items
- **Real-time Updates**: Automatic cart total and item count updates
- **Quantity Control**: Adjust item quantities with validation
- **Checkout Process**: Streamlined checkout with order confirmation

### 💬 Chat Interface
- **Natural Language Processing**: Type shopping requests in plain English
- **Smart Commands**: Supports add, remove, search, and help commands
- **Real Cart Integration**: Chat commands actually update your cart
- **Conversation History**: Track your shopping conversation
- **Quick Actions**: Pre-built buttons for common requests

#### Chat Examples:
```
"Add a red shirt to my cart"
"Show me my cart" 
"Search for blue jeans under $100"
"Remove the last item"
"Clear my cart"
"Help me shop"
```

### 🧪 Testing Tools
- **End-to-End Tests**: Run comprehensive system tests
- **Scenario Testing**: Execute predefined shopping scenarios
- **Performance Metrics**: View success rates and processing times
- **Manual Testing**: Test individual commands and responses

### 📊 Analytics Dashboard
- **Product Analytics**: Category distribution and price analysis
- **Brand Insights**: Top brands and product counts
- **Stock Analysis**: Inventory status and availability rates
- **Session Analytics**: Cart activity and conversation patterns

## Getting Started

### Prerequisites
```bash
pip install streamlit plotly pandas
```

### Running the GUI

#### Option 1: Using the launcher script
```bash
python run_gui.py
```

#### Option 2: Direct Streamlit command
```bash
streamlit run voice_shopping_assistant/gui/streamlit_app.py
```

#### Option 3: From project root
```bash
cd voice_shopping_assistant/gui
streamlit run streamlit_app.py
```

The GUI will open in your browser at `http://localhost:8501`

## Usage Guide

### Navigation
Use the sidebar to navigate between different sections:
- 🏠 **Home**: Overview and quick actions
- 🛍️ **Shop Products**: Browse and search products
- 🛒 **Shopping Cart**: Manage your cart
- 💬 **Chat Interface**: Natural language shopping
- 🧪 **Testing Tools**: System testing and validation
- 📊 **Analytics**: Insights and metrics

### Shopping Workflow

1. **Browse Products**: Use the Shop Products page to explore the catalog
2. **Add Items**: Click "Add to Cart" or use chat commands
3. **Manage Cart**: View and modify items in the Shopping Cart
4. **Chat Shopping**: Use natural language in the Chat Interface
5. **Checkout**: Complete your purchase from the cart page

### Chat Commands

The chat interface supports natural language commands:

**Adding Items:**
- "Add [quantity] [color] [product] to my cart"
- "I want some [product]"
- "Put [product] in my cart"

**Cart Management:**
- "Show me my cart"
- "What's in my cart?"
- "Remove [item]" or "Remove the last item"
- "Clear my cart"

**Product Search:**
- "Search for [product]"
- "Find me [product] under $[price]"
- "Show me [category] products"

**Help:**
- "Help me shop"
- "What can you do?"

## Technical Details

### Architecture
- **Frontend**: Streamlit web framework
- **Backend**: Voice Shopping Assistant core components
- **Data**: Sample product catalog with 32+ products
- **State Management**: Streamlit session state for cart persistence
- **Visualization**: Plotly charts for analytics

### Components
- `VoiceShoppingGUI`: Main application class
- `process_shopping_command()`: Natural language command processor
- `handle_*_command()`: Specific command handlers
- Product search and filtering system
- Cart management with validation

### Session Management
- Each browser session maintains its own cart
- Conversation history is preserved during the session
- Session state includes cart items, conversation history, and preferences

### Product Catalog
- 32+ diverse products across 12 categories
- Price range: $12.99 - $1,299.99
- Realistic attributes: colors, sizes, materials, brands
- Stock status simulation

## Customization

### Adding Products
Modify `voice_shopping_assistant/testing/sample_catalog.py` to add new products:

```python
new_product = Product(
    id="custom-001",
    name="Custom Product",
    category="custom",
    price=99.99,
    available_sizes=["one size"],
    available_colors=["blue"],
    material="custom material", 
    brand="CustomBrand",
    in_stock=True
)
```

### Styling
Customize the appearance by modifying the CSS in `streamlit_app.py`:

```python
st.markdown("""
<style>
    .custom-style {
        /* Your custom CSS */
    }
</style>
""", unsafe_allow_html=True)
```

### Chat Commands
Extend chat functionality by adding new handlers in the `process_shopping_command()` method.

## Troubleshooting

### Common Issues

**GUI won't start:**
- Ensure Streamlit is installed: `pip install streamlit`
- Check Python version compatibility (3.7+)
- Verify all dependencies are installed

**Chat not updating cart:**
- This has been fixed in the latest version
- Chat commands now properly integrate with cart management
- Refresh the page if issues persist

**Products not loading:**
- Check that the sample catalog is properly imported
- Verify the testing module is accessible
- Restart the Streamlit server

**Performance issues:**
- Reduce the number of products displayed
- Use filters to limit search results
- Clear browser cache if needed

### Debug Mode
Run with debug logging:
```bash
streamlit run streamlit_app.py --logger.level=debug
```

## Development

### Project Structure
```
voice_shopping_assistant/gui/
├── streamlit_app.py      # Main GUI application
├── __init__.py          # Module initialization
└── README.md           # This documentation
```

### Contributing
1. Follow the existing code style
2. Test changes with both GUI and command-line interfaces
3. Update documentation for new features
4. Ensure chat integration works properly

## Future Enhancements

- **Voice Input**: Add speech-to-text capability
- **User Accounts**: Persistent shopping history
- **Payment Integration**: Real checkout processing
- **Product Images**: Visual product catalog
- **Mobile Optimization**: Responsive design improvements
- **Real-time Updates**: WebSocket-based cart synchronization

## Support

For issues or questions:
1. Check this README for common solutions
2. Review the main project documentation
3. Test with the command-line interface first
4. Check browser console for JavaScript errors

The GUI provides a complete shopping experience with natural language interaction, making it easy to browse products, manage your cart, and complete purchases through an intuitive web interface.