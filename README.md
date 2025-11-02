# 🛒 Voice Shopping Assistant

A comprehensive AI-powered shopping assistant with voice recognition, natural language processing, and a modern web interface. Shop naturally using voice commands or text input with real-time cart management and smart product search.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-v1.28+-red.svg)
![FastAPI](https://img.shields.io/badge/fastapi-v0.104+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## ✨ Features

### 🎤 **Voice Integration**
- **Speech-to-Text**: Browser-based Web Speech API integration
- **Automatic Processing**: Voice commands execute immediately
- **Natural Language**: Speak naturally - "Add two red shirts to my cart"
- **Real-time Feedback**: Visual status indicators and transcription

### 🧠 **Smart NLP Processing**
- **Intent Classification**: Understands add, remove, search, help commands
- **Entity Extraction**: Recognizes products, colors, sizes, quantities, prices
- **Context Awareness**: Maintains conversation context and cart state
- **Fuzzy Matching**: Handles variations in speech and text input

### 🛒 **Advanced Cart Management**
- **Real-time Updates**: Instant cart synchronization across interfaces
- **Smart Validation**: Prevents invalid operations and provides suggestions
- **Session Persistence**: Maintains cart state during browser session
- **Quantity Management**: Add, remove, update item quantities

### 🔍 **Intelligent Product Search**
- **32+ Sample Products**: Diverse catalog across multiple categories
- **Advanced Filtering**: Search by name, category, price, brand, material
- **Price Constraints**: "Show me jeans under $100"
- **Fuzzy Search**: Finds products even with typos or partial matches

### 🖥️ **Modern Web Interface**
- **Multi-page GUI**: Home, Products, Cart, Chat, Testing, Analytics
- **Responsive Design**: Works on desktop and mobile browsers
- **Interactive Charts**: Product analytics and insights
- **Real-time Updates**: Live cart and conversation updates

### 🚀 **REST API**
- **FastAPI Backend**: High-performance async API
- **Full CRUD Operations**: Complete cart and product management
- **API Documentation**: Auto-generated OpenAPI/Swagger docs
- **Health Monitoring**: System status and performance metrics

### 🧪 **Comprehensive Testing**
- **End-to-End Testing**: Complete workflow validation
- **Conversation Simulation**: Automated chat testing
- **Performance Metrics**: Success rates and processing times
- **Sample Data**: Rich product catalog for testing

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Modern web browser (Chrome, Edge, Safari recommended for voice)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/voice-shopping-assistant.git
   cd voice-shopping-assistant
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install GUI dependencies** (optional)
   ```bash
   pip install -r gui_requirements.txt
   ```

### Running the Application

#### 🖥️ **Web GUI (Recommended)**
```bash
python run_gui.py
```
- Opens at `http://localhost:8501`
- Full voice and text interface
- Complete shopping experience

#### 🌐 **REST API**
```bash
python run_api.py
```
- API at `http://localhost:8000`
- Swagger docs at `http://localhost:8000/docs`
- Programmatic access

#### 🧪 **Run Tests**
```bash
python test_end_to_end.py
```

## 🎤 Voice Commands

### Shopping Commands
- *"Add a red shirt to my cart"*
- *"Add two blue jeans size 32"*
- *"Put some headphones in my cart"*

### Search Commands  
- *"Show me blue jeans under $100"*
- *"Find red shirts"*
- *"Search for laptops"*

### Cart Management
- *"Show me my cart"*
- *"Remove the last item"*
- *"Clear my cart"*

### Help Commands
- *"Help me shop"*
- *"What can you do?"*

## 📁 Project Structure

```
voice-shopping-assistant/
├── 🎤 voice_shopping_assistant/
│   ├── asr/              # Speech Recognition
│   ├── nlp/              # Natural Language Processing  
│   ├── cart/             # Shopping Cart Logic
│   ├── response/         # Response Generation
│   ├── api/              # REST API (FastAPI)
│   ├── gui/              # Web Interface (Streamlit)
│   ├── testing/          # Testing Framework
│   └── config/           # Configuration
├── 📋 .kiro/specs/       # Project Specifications
├── 🧪 test_*.py         # Test Scripts
├── 🚀 run_gui.py         # GUI Launcher
├── 🌐 run_api.py         # API Launcher
└── 📚 README.md          # This file
```

## 🖥️ GUI Interface

### Pages Available:
- **🏠 Home**: Dashboard with quick actions and overview
- **🛍️ Shop Products**: Browse and search 32+ products  
- **🛒 Shopping Cart**: Manage cart items and checkout
- **💬 Chat Interface**: Voice and text shopping commands
- **🧪 Testing Tools**: Run system tests and scenarios
- **📊 Analytics**: Product insights and usage metrics

### Browser Support:
| Browser | Voice Support | GUI Support |
|---------|---------------|-------------|
| ✅ Chrome | Full | Full |
| ✅ Edge | Full | Full |
| ✅ Safari | Full | Full |
| ⚠️ Firefox | Limited | Full |

## 🌐 API Endpoints

### Core Endpoints:
- `POST /api/v1/text/process` - Process text commands
- `GET /api/v1/cart/{session_id}` - Get cart contents
- `POST /api/v1/cart/add` - Add items to cart
- `POST /api/v1/products/search` - Search products
- `GET /api/v1/health` - System health check

### Documentation:
- Interactive API docs: `http://localhost:8000/docs`
- OpenAPI spec: `http://localhost:8000/openapi.json`

## 🧪 Testing

### Run All Tests:
```bash
python test_end_to_end.py
```

### Test Categories:
- **API Tests**: `python test_api_basic.py`
- **Integration Tests**: `python test_api_integration.py`  
- **GUI Tests**: `python demo_gui.py`

### Sample Test Results:
```
✅ All tests PASSED! (Success rate: 100.0%)
📊 Performance Metrics:
   - Average Intent Accuracy: 94.4%
   - Average Processing Time: 0.001s
   - Command Success Rate: 92.3%
```

## 🛠️ Development

### Adding New Products:
```python
from voice_shopping_assistant.testing.sample_catalog import SampleProductCatalog
from voice_shopping_assistant.models.core import Product

new_product = Product(
    id="custom-001",
    name="Custom Product",
    category="electronics",
    price=99.99,
    available_sizes=["one size"],
    available_colors=["black", "white"],
    material="plastic",
    brand="CustomBrand",
    in_stock=True
)
```

### Extending Voice Commands:
Modify `voice_shopping_assistant/gui/streamlit_app.py`:
```python
def handle_custom_command(self, user_input: str) -> str:
    # Add your custom command logic
    return "Custom response"
```

## 📊 Sample Data

The system includes a rich product catalog:
- **32+ Products** across 12 categories
- **Price Range**: $12.99 - $1,299.99
- **Categories**: Clothing, Electronics, Home, Sports, Books, Beauty, Toys, Food
- **Realistic Attributes**: Colors, sizes, materials, brands, stock status

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Streamlit** for the amazing web framework
- **FastAPI** for the high-performance API framework
- **Web Speech API** for browser-based speech recognition
- **Plotly** for interactive data visualizations

## 📞 Support

- 📧 **Issues**: [GitHub Issues](https://github.com/yourusername/voice-shopping-assistant/issues)
- 📖 **Documentation**: See individual README files in each module
- 💬 **Discussions**: [GitHub Discussions](https://github.com/yourusername/voice-shopping-assistant/discussions)

---

**🎉 Start shopping with your voice today!** 

Try saying: *"Add a blue shirt to my cart"* and watch the magic happen! ✨