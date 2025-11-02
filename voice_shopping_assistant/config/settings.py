"""Configuration management for the voice shopping assistant"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import json
from dataclasses import dataclass, asdict


@dataclass
class ASRConfig:
    """ASR engine configuration"""
    whisper_model_size: str = "small"
    whisper_model_path: Optional[str] = None
    confidence_threshold: float = 0.7
    max_audio_length: int = 30  # seconds
    sample_rate: int = 16000
    fallback_enabled: bool = True
    google_api_key: Optional[str] = None


@dataclass
class NLPConfig:
    """NLP processing configuration"""
    intent_model_path: str = "distilbert-base-uncased"
    entity_model_path: str = "en_core_web_sm"
    intent_confidence_threshold: float = 0.8
    entity_confidence_threshold: float = 0.7
    max_text_length: int = 512
    enable_context_resolution: bool = True


@dataclass
class CartConfig:
    """Cart management configuration"""
    max_cart_items: int = 50
    session_timeout: int = 1800  # 30 minutes in seconds
    enable_inventory_check: bool = True
    max_quantity_per_item: int = 10
    price_precision: int = 2


@dataclass
class APIConfig:
    """API service configuration"""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    cors_origins: list = None
    max_request_size: int = 10 * 1024 * 1024  # 10MB
    request_timeout: int = 30
    
    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["*"]


@dataclass
class PerformanceConfig:
    """Performance and optimization settings"""
    enable_caching: bool = True
    cache_ttl: int = 300  # 5 minutes
    max_concurrent_requests: int = 100
    model_batch_size: int = 1
    gpu_enabled: bool = False
    cpu_threads: int = 4


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5


class Settings:
    """Main settings class that manages all configuration"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or self._get_default_config_path()
        
        # Initialize with defaults
        self.asr = ASRConfig()
        self.nlp = NLPConfig()
        self.cart = CartConfig()
        self.api = APIConfig()
        self.performance = PerformanceConfig()
        self.logging = LoggingConfig()
        
        # Load from file if exists
        self.load_config()
        
        # Override with environment variables
        self._load_from_env()
    
    def _get_default_config_path(self) -> str:
        """Get default configuration file path"""
        return os.path.join(os.getcwd(), "config.json")
    
    def load_config(self) -> None:
        """Load configuration from JSON file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                
                # Update each section if present
                if 'asr' in config_data:
                    self._update_config(self.asr, config_data['asr'])
                if 'nlp' in config_data:
                    self._update_config(self.nlp, config_data['nlp'])
                if 'cart' in config_data:
                    self._update_config(self.cart, config_data['cart'])
                if 'api' in config_data:
                    self._update_config(self.api, config_data['api'])
                if 'performance' in config_data:
                    self._update_config(self.performance, config_data['performance'])
                if 'logging' in config_data:
                    self._update_config(self.logging, config_data['logging'])
                    
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Warning: Could not load config file {self.config_file}: {e}")
    
    def _update_config(self, config_obj, config_dict: Dict[str, Any]) -> None:
        """Update configuration object with dictionary values"""
        for key, value in config_dict.items():
            if hasattr(config_obj, key):
                setattr(config_obj, key, value)
    
    def _load_from_env(self) -> None:
        """Load configuration from environment variables"""
        # ASR settings
        if os.getenv('WHISPER_MODEL_SIZE'):
            self.asr.whisper_model_size = os.getenv('WHISPER_MODEL_SIZE')
        if os.getenv('WHISPER_MODEL_PATH'):
            self.asr.whisper_model_path = os.getenv('WHISPER_MODEL_PATH')
        if os.getenv('ASR_CONFIDENCE_THRESHOLD'):
            self.asr.confidence_threshold = float(os.getenv('ASR_CONFIDENCE_THRESHOLD'))
        if os.getenv('GOOGLE_API_KEY'):
            self.asr.google_api_key = os.getenv('GOOGLE_API_KEY')
        
        # NLP settings
        if os.getenv('INTENT_MODEL_PATH'):
            self.nlp.intent_model_path = os.getenv('INTENT_MODEL_PATH')
        if os.getenv('ENTITY_MODEL_PATH'):
            self.nlp.entity_model_path = os.getenv('ENTITY_MODEL_PATH')
        
        # API settings
        if os.getenv('API_HOST'):
            self.api.host = os.getenv('API_HOST')
        if os.getenv('API_PORT'):
            self.api.port = int(os.getenv('API_PORT'))
        if os.getenv('API_DEBUG'):
            self.api.debug = os.getenv('API_DEBUG').lower() == 'true'
        
        # Performance settings
        if os.getenv('GPU_ENABLED'):
            self.performance.gpu_enabled = os.getenv('GPU_ENABLED').lower() == 'true'
        if os.getenv('CPU_THREADS'):
            self.performance.cpu_threads = int(os.getenv('CPU_THREADS'))
        
        # Logging settings
        if os.getenv('LOG_LEVEL'):
            self.logging.level = os.getenv('LOG_LEVEL')
        if os.getenv('LOG_FILE'):
            self.logging.file_path = os.getenv('LOG_FILE')
    
    def save_config(self) -> None:
        """Save current configuration to JSON file"""
        config_data = {
            'asr': asdict(self.asr),
            'nlp': asdict(self.nlp),
            'cart': asdict(self.cart),
            'api': asdict(self.api),
            'performance': asdict(self.performance),
            'logging': asdict(self.logging)
        }
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
        
        with open(self.config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    def get_model_paths(self) -> Dict[str, str]:
        """Get all model paths for easy access"""
        return {
            'whisper_model': self.asr.whisper_model_path or f"openai/whisper-{self.asr.whisper_model_size}",
            'intent_model': self.nlp.intent_model_path,
            'entity_model': self.nlp.entity_model_path
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert all settings to dictionary"""
        return {
            'asr': asdict(self.asr),
            'nlp': asdict(self.nlp),
            'cart': asdict(self.cart),
            'api': asdict(self.api),
            'performance': asdict(self.performance),
            'logging': asdict(self.logging)
        }


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get the global settings instance"""
    return settings


def reload_settings(config_file: Optional[str] = None) -> Settings:
    """Reload settings from file"""
    global settings
    settings = Settings(config_file)
    return settings