#!/usr/bin/env python3
"""
Startup script for Voice Shopping Assistant API

This script starts the FastAPI server with proper configuration and error handling.
"""

import sys
import os
import logging
import argparse
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    import uvicorn
    from voice_shopping_assistant.config.settings import get_settings
    from voice_shopping_assistant.api.app import app
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please ensure all dependencies are installed:")
    print("pip install -r requirements.txt")
    sys.exit(1)


def setup_logging(debug: bool = False):
    """Setup logging configuration"""
    log_level = logging.DEBUG if debug else logging.INFO
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('api.log', mode='a')
        ]
    )
    
    # Reduce noise from some libraries
    logging.getLogger('uvicorn.access').setLevel(logging.WARNING)
    if not debug:
        logging.getLogger('transformers').setLevel(logging.WARNING)
        logging.getLogger('torch').setLevel(logging.WARNING)


def check_dependencies():
    """Check if required dependencies are available"""
    required_modules = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'transformers',
        'torch',
        'whisper',
        'spacy'
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print("Missing required dependencies:")
        for module in missing_modules:
            print(f"  - {module}")
        print("\nPlease install missing dependencies:")
        print("pip install -r requirements.txt")
        return False
    
    return True


def check_models():
    """Check if required models are available"""
    try:
        # Check if spaCy model is available
        import spacy
        try:
            spacy.load("en_core_web_sm")
        except OSError:
            print("spaCy English model not found. Installing...")
            os.system("python -m spacy download en_core_web_sm")
        
        # Check Whisper model (will be downloaded on first use)
        import whisper
        print("Whisper models will be downloaded automatically on first use")
        
        return True
        
    except Exception as e:
        print(f"Error checking models: {e}")
        return False


def download_nltk_data():
    """Download required NLTK data"""
    try:
        import nltk
        
        # Download required NLTK data
        nltk_downloads = [
            'punkt',
            'stopwords',
            'wordnet',
            'averaged_perceptron_tagger',
            'vader_lexicon'
        ]
        
        for item in nltk_downloads:
            try:
                nltk.download(item, quiet=True)
            except Exception as e:
                print(f"Warning: Could not download NLTK data '{item}': {e}")
        
        return True
        
    except Exception as e:
        print(f"Warning: NLTK data download failed: {e}")
        return False


def initialize_ml_models():
    """Initialize ML models to check they work"""
    try:
        print("Initializing ML models...")
        
        # Test Whisper
        print("  Testing Whisper...")
        import whisper
        # Just load the model info, don't actually load the model
        print("    ✓ Whisper available")
        
        # Test Transformers
        print("  Testing Transformers...")
        from transformers import pipeline
        print("    ✓ Transformers available")
        
        # Test spaCy
        print("  Testing spaCy...")
        import spacy
        try:
            nlp = spacy.load("en_core_web_sm")
            print("    ✓ spaCy model loaded")
        except OSError:
            print("    ⚠ spaCy model not found, but spaCy is available")
        
        return True
        
    except Exception as e:
        print(f"ML model initialization failed: {e}")
        return False


def main():
    """Main function to start the API server"""
    parser = argparse.ArgumentParser(description="Voice Shopping Assistant API Server")
    parser.add_argument("--host", default=None, help="Host to bind to")
    parser.add_argument("--port", type=int, default=None, help="Port to bind to")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--workers", type=int, default=1, help="Number of worker processes")
    parser.add_argument("--check-only", action="store_true", help="Only check dependencies and exit")
    parser.add_argument("--skip-ml-init", action="store_true", help="Skip ML model initialization")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.debug)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Voice Shopping Assistant API...")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check models
    if not check_models():
        logger.warning("Some models may not be available, but continuing...")
    
    # Download NLTK data
    if not args.skip_ml_init:
        download_nltk_data()
        
        # Initialize ML models
        if not initialize_ml_models():
            logger.warning("ML model initialization failed, but continuing...")
    
    if args.check_only:
        print("✓ All dependencies are available")
        sys.exit(0)
    
    # Get settings
    try:
        settings = get_settings()
    except Exception as e:
        logger.error(f"Failed to load settings: {e}")
        sys.exit(1)
    
    # Override settings with command line arguments
    host = args.host or settings.api.host
    port = args.port or settings.api.port
    debug = args.debug or settings.api.debug
    
    logger.info(f"Configuration:")
    logger.info(f"  Host: {host}")
    logger.info(f"  Port: {port}")
    logger.info(f"  Debug: {debug}")
    logger.info(f"  Workers: {args.workers}")
    logger.info(f"  Reload: {args.reload}")
    
    # Print startup information
    print("\n" + "="*60)
    print("🎤 Voice Shopping Assistant API Server")
    print("="*60)
    print(f"Server will start at: http://{host}:{port}")
    print(f"API Documentation: http://{host}:{port}/docs")
    print(f"Health Check: http://{host}:{port}/api/v1/health")
    print(f"Performance Metrics: http://{host}:{port}/api/v1/performance")
    print("="*60)
    
    # Start the server
    try:
        uvicorn.run(
            "voice_shopping_assistant.api.app:app",
            host=host,
            port=port,
            debug=debug,
            reload=args.reload,
            workers=args.workers if not args.reload else 1,  # Can't use workers with reload
            log_level="debug" if debug else "info",
            access_log=True,
            loop="asyncio"
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        print("\n👋 Voice Shopping Assistant API stopped")
    except Exception as e:
        logger.error(f"Server failed to start: {e}")
        print(f"\n❌ Server failed to start: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()