# Voice Shopping Assistant API

A comprehensive REST API for voice-enabled shopping with natural language processing capabilities.

## 🚀 Features

- **Voice Command Processing**: Convert speech to shopping actions using Whisper ASR
- **Text Command Processing**: Direct text input for testing and integration
- **Cart Management**: Add, remove, update, and view cart items with validation
- **Product Search**: Search and filter products with various criteria
- **Session Management**: Maintain conversation context across requests
- **Performance Monitoring**: Real-time metrics and performance tracking
- **Error Handling**: Comprehensive error responses with helpful guidance

## 📋 Requirements

### System Requirements
- Python 3.8+
- 4GB+ RAM (for ML models)
- 2GB+ disk space (for model downloads)

### Dependencies
- FastAPI & Uvicorn (API framework)
- PyTorch (ML backend)
- Transformers (NLP models)
- OpenAI Whisper (Speech recognition)
- spaCy (Entity extraction)
- scikit-learn (ML utilities)

## 🛠️ Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd voice-shopping-assistant
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Download ML Models
```bash
# Download spaCy English model
python -m spacy download en_core_web_sm

# Whisper models will be downloaded automatically on first use
```

## 🚀 Quick Start

### 1. Start the API Server
```bash
python run_api.py
```

The server will start at `http://localhost:8000`

### 2. Check API Health
```bash
curl http://localhost:8000/api/v1/health
```

### 3. Process Text Command
```bash
curl -X POST "http://localhost:8000/api/v1/text/process" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "demo-session",
    "text": "add two red shirts to my cart"
  }'
```

### 4. Run Demo
```bash
python demo_api.py
```

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Core Endpoints

#### Voice Processing
- `POST /api/v1/voice/process` - Process voice command with audio data
- `POST /api/v1/text/process` - Process text command directly
- `POST /api/v1/voice/upload` - Upload and process audio file

#### Cart Management
- `GET /api/v1/cart/{session_id}` - Get cart contents
- `POST /api/v1/cart/add` - Add items to cart
- `POST /api/v1/cart/remove` - Remove items from cart
- `PUT /api/v1/cart/update` - Update item quantities
- `DELETE /api/v1/cart/{session_id}` - Clear cart

#### Product Search
- `POST /api/v1/products/search` - Search products
- `GET /api/v1/products/{product_id}` - Get product details

#### System & Monitoring
- `GET /api/v1/health` - Health check
- `GET /api/v1/stats` - API statistics
- `GET /api/v1/performance` - Performance metrics
- `GET /api/v1/sessions/{session_id}` - Session information

## 🎯 Usage Examples

### Text Command Processing
```python
import requests

response = requests.post("http://localhost:8000/api/v1/text/process", json={
    "session_id": "user-123",
    "text": "add three blue jeans to my cart"
})

result = response.json()
print(f"Response: {result['response_text']}")
print(f"Intent: {result['intent']['type']}")
```

### Voice Command Processing
```python
import requests
import base64

# Read audio file
with open("voice_command.wav", "rb") as f:
    audio_data = base64.b64encode(f.read()).decode()

response = requests.post("http://localhost:8000/api/v1/voice/process", json={
    "session_id": "user-123",
    "audio_data": audio_data
})

result = response.json()
print(f"Transcribed: {result['original_text']}")
print(f"Response: {result['response_text']}")
```

### Cart Management
```python
import requests

# Add items to cart
requests.post("http://localhost:8000/api/v1/cart/add", json={
    "session_id": "user-123",
    "items": [{
        "product_id": "shirt-001",
        "quantity": 2,
        "size": "M",
        "color": "red"
    }]
})

# Get cart contents
response = requests.get("http://localhost:8000/api/v1/cart/user-123")
cart = response.json()
print(f"Cart total: ₹{cart['cart_summary']['total_price']}")
```

### Product Search
```python
import requests

# Search by query
response = requests.post("http://localhost:8000/api/v1/products/search", json={
    "query": "red shirt",
    "limit": 10
})

products = response.json()
for product in products['products']:
    print(f"{product['name']} - ₹{product['price']}")

# Search with filters
response = requests.post("http://localhost:8000/api/v1/products/search", json={
    "filters": {
        "category": "clothing",
        "color": "red",
        "min_price": 500,
        "max_price": 2000
    }
})
```

## 🔧 Configuration

### Environment Variables
```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=false

# Model Configuration
WHISPER_MODEL_SIZE=small
ASR_CONFIDENCE_THRESHOLD=0.7

# Performance
GPU_ENABLED=false
CPU_THREADS=4
```

### Configuration File
Create `config.json` in the project root:
```json
{
  "api": {
    "host": "0.0.0.0",
    "port": 8000,
    "debug": false,
    "cors_origins": ["*"]
  },
  "asr": {
    "whisper_model_size": "small",
    "confidence_threshold": 0.7
  },
  "nlp": {
    "intent_confidence_threshold": 0.8,
    "entity_confidence_threshold": 0.7
  }
}
```

## 📊 Monitoring & Performance

### Health Monitoring
```bash
# Basic health check
curl http://localhost:8000/api/v1/health

# Detailed performance metrics
curl http://localhost:8000/api/v1/performance

# API statistics
curl http://localhost:8000/api/v1/stats
```

### Performance Metrics
The API tracks:
- Request/response times
- Success/error rates
- Endpoint-specific statistics
- Session activity
- Slow request detection
- Error rate alerts

### Logging
Logs are written to:
- Console (structured logging)
- `api.log` file
- Performance metrics in memory

## 🧪 Testing

### Run Integration Tests
```bash
python test_api_integration.py
```

### Run Basic Structure Tests
```bash
python test_api_basic.py
```

### Manual Testing with Demo
```bash
# Full demo
python demo_api.py

# Single command test
python demo_api.py --command "add shirt to cart"
```

## 🚀 Deployment

### Development Server
```bash
python run_api.py --debug --reload
```

### Production Server
```bash
python run_api.py --workers 4 --host 0.0.0.0 --port 8000
```

### Docker Deployment
```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python -m spacy download en_core_web_sm

EXPOSE 8000
CMD ["python", "run_api.py", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Considerations
- Use a reverse proxy (nginx)
- Enable HTTPS
- Set up proper logging
- Configure rate limiting
- Monitor resource usage
- Set up health checks

## 🔒 Security

### Authentication
Currently uses session-based identification. For production:
- Implement JWT tokens
- Add API key authentication
- Set up OAuth2 integration

### Rate Limiting
Default: 60 requests per minute per IP
Configure in middleware settings.

### Input Validation
- Request size limits (10MB)
- Content type validation
- Input sanitization
- SQL injection prevention

## 🐛 Troubleshooting

### Common Issues

#### 1. Model Loading Errors
```bash
# Download missing models
python -m spacy download en_core_web_sm
pip install torch torchvision torchaudio
```

#### 2. Memory Issues
- Reduce Whisper model size: `WHISPER_MODEL_SIZE=tiny`
- Disable GPU: `GPU_ENABLED=false`
- Increase system RAM

#### 3. Performance Issues
- Enable GPU if available
- Reduce concurrent requests
- Optimize model sizes
- Check system resources

#### 4. Connection Issues
- Check firewall settings
- Verify port availability
- Check network configuration

### Debug Mode
```bash
python run_api.py --debug
```

### Logs Analysis
```bash
# View recent logs
tail -f api.log

# Search for errors
grep ERROR api.log
```

## 📈 Performance Optimization

### Model Optimization
- Use smaller Whisper models for faster processing
- Enable GPU acceleration when available
- Cache frequently used models
- Batch process requests when possible

### API Optimization
- Enable response compression
- Use connection pooling
- Implement caching for search results
- Optimize database queries

### Monitoring
- Set up performance alerts
- Monitor resource usage
- Track response times
- Analyze error patterns

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest

# Format code
black voice_shopping_assistant/
flake8 voice_shopping_assistant/
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Check the `/docs` endpoint
- **Issues**: Create GitHub issues for bugs
- **Performance**: Use `/api/v1/performance` for metrics
- **Health**: Monitor `/api/v1/health` endpoint

## 🔄 API Versioning

Current version: v1
- Backward compatibility maintained
- Deprecation notices provided
- Migration guides available

---

**Happy Shopping! 🛒🎤**