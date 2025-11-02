# Contributing to Voice Shopping Assistant

Thank you for your interest in contributing to the Voice Shopping Assistant! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Git
- Modern web browser (Chrome, Edge, Safari for voice features)

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/yourusername/voice-shopping-assistant.git
   cd voice-shopping-assistant
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r gui_requirements.txt
   ```

4. **Run tests to ensure everything works**
   ```bash
   python test_end_to_end.py
   python test_api_basic.py
   ```

## 🛠️ Development Guidelines

### Code Style
- Follow PEP 8 Python style guidelines
- Use type hints where possible
- Write docstrings for all public functions and classes
- Keep functions focused and small (< 50 lines when possible)

### Testing
- Write tests for new features
- Ensure all existing tests pass
- Aim for good test coverage of core functionality
- Test both API and GUI components

### Documentation
- Update README.md for significant changes
- Add docstrings to new functions and classes
- Update relevant documentation in module README files

## 📝 How to Contribute

### Reporting Bugs

1. **Check existing issues** to avoid duplicates
2. **Use the bug report template** when creating issues
3. **Include detailed information**:
   - Python version
   - Operating system
   - Browser (for GUI issues)
   - Steps to reproduce
   - Expected vs actual behavior
   - Error messages or logs

### Suggesting Features

1. **Check existing feature requests** to avoid duplicates
2. **Use the feature request template**
3. **Provide detailed description**:
   - Use case and motivation
   - Proposed solution
   - Alternative solutions considered
   - Additional context

### Submitting Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow the coding guidelines
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   python test_end_to_end.py
   python test_api_basic.py
   python demo_gui.py
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: your feature description"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**
   - Use the PR template
   - Provide clear description of changes
   - Link related issues
   - Request review from maintainers

## 🎯 Areas for Contribution

### High Priority
- **Voice Recognition Improvements**: Better speech processing accuracy
- **NLP Enhancements**: More sophisticated intent classification
- **Product Catalog**: Expand the sample product database
- **Mobile Support**: Improve mobile browser compatibility
- **Performance**: Optimize processing speed and memory usage

### Medium Priority
- **New Voice Commands**: Add support for more shopping operations
- **UI/UX Improvements**: Enhance the Streamlit interface
- **API Extensions**: Add new endpoints and functionality
- **Testing**: Expand test coverage and scenarios
- **Documentation**: Improve guides and examples

### Good First Issues
- **Bug fixes**: Small, well-defined issues
- **Documentation updates**: Fix typos, improve clarity
- **Test additions**: Add tests for existing functionality
- **Sample data**: Add more products to the catalog
- **Code cleanup**: Refactor and improve code quality

## 🏗️ Project Structure

```
voice-shopping-assistant/
├── voice_shopping_assistant/
│   ├── asr/              # Speech Recognition
│   ├── nlp/              # Natural Language Processing
│   ├── cart/             # Shopping Cart Logic
│   ├── response/         # Response Generation
│   ├── api/              # REST API
│   ├── gui/              # Web Interface
│   ├── testing/          # Testing Framework
│   └── config/           # Configuration
├── tests/                # Test files
├── docs/                 # Documentation
└── scripts/              # Utility scripts
```

### Key Components

- **GUI (`gui/streamlit_app.py`)**: Main web interface
- **API (`api/app.py`)**: REST API server
- **Models (`models/core.py`)**: Data models and schemas
- **Testing (`testing/`)**: Test framework and sample data
- **Cart (`cart/`)**: Shopping cart management
- **NLP (`nlp/`)**: Natural language processing

## 🧪 Testing Guidelines

### Running Tests
```bash
# Run all tests
python test_end_to_end.py

# Run API tests
python test_api_basic.py
python test_api_integration.py

# Run GUI tests
python demo_gui.py

# Test specific functionality
python test_chat_fixes.py
python test_search_fix.py
```

### Writing Tests
- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies when appropriate
- Keep tests independent and isolated

## 📋 Pull Request Guidelines

### PR Checklist
- [ ] Code follows project style guidelines
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Documentation updated as needed
- [ ] PR description clearly explains changes
- [ ] Related issues are linked

### PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass
- [ ] New tests added
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
```

## 🤝 Community Guidelines

### Code of Conduct
- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect different opinions and approaches

### Communication
- Use clear, descriptive commit messages
- Provide context in PR descriptions
- Be responsive to feedback and questions
- Ask for help when needed

## 🏷️ Issue Labels

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements or additions to docs
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention is needed
- `question`: Further information is requested
- `wontfix`: This will not be worked on

## 📞 Getting Help

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Documentation**: Check README files in each module
- **Code Comments**: Look at inline documentation

## 🎉 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes for significant contributions
- GitHub contributor graphs

Thank you for contributing to the Voice Shopping Assistant! 🛒✨