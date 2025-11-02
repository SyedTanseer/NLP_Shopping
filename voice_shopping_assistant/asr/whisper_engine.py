"""Whisper ASR engine implementation"""

import time
import logging
from typing import Iterator, Optional, Union
import numpy as np
import whisper
import torch
from io import BytesIO
import wave
import tempfile
import os

from ..interfaces import ASREngineInterface
from ..models.core import TranscriptionResult
from ..config.settings import get_settings


logger = logging.getLogger(__name__)


class WhisperASREngine(ASREngineInterface):
    """Whisper-based ASR engine implementation"""
    
    def __init__(self, model_size: Optional[str] = None, device: Optional[str] = None):
        """Initialize Whisper ASR engine
        
        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
            device: Device to run model on (cpu, cuda)
        """
        self.settings = get_settings()
        self.model_size = model_size or self.settings.asr.whisper_model_size
        self.device = device or ("cuda" if torch.cuda.is_available() and self.settings.performance.gpu_enabled else "cpu")
        self.confidence_threshold = self.settings.asr.confidence_threshold
        self.max_audio_length = self.settings.asr.max_audio_length
        self.sample_rate = self.settings.asr.sample_rate
        
        self.model = None
        self._load_model()
    
    def _load_model(self) -> None:
        """Load Whisper model"""
        try:
            logger.info(f"Loading Whisper model: {self.model_size} on {self.device}")
            self.model = whisper.load_model(self.model_size, device=self.device)
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise RuntimeError(f"Could not load Whisper model: {e}")
    
    def _validate_audio_data(self, audio_data: bytes) -> bool:
        """Validate audio data format and length
        
        Args:
            audio_data: Raw audio bytes
            
        Returns:
            True if valid, False otherwise
        """
        if not audio_data or len(audio_data) == 0:
            logger.warning("Empty audio data provided")
            return False
        
        # Check if audio data is too large (basic size check)
        max_size = self.max_audio_length * self.sample_rate * 2  # 2 bytes per sample for 16-bit
        if len(audio_data) > max_size:
            logger.warning(f"Audio data too large: {len(audio_data)} bytes (max: {max_size})")
            return False
        
        return True
    
    def _preprocess_audio(self, audio_data: bytes) -> np.ndarray:
        """Preprocess audio data for Whisper
        
        Args:
            audio_data: Raw audio bytes
            
        Returns:
            Preprocessed audio array
        """
        try:
            # Create temporary WAV file for processing
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name
            
            try:
                # Load audio using whisper's built-in loader
                audio_array = whisper.load_audio(temp_path)
                
                # Ensure audio is within length limits
                max_samples = self.max_audio_length * self.sample_rate
                if len(audio_array) > max_samples:
                    logger.warning(f"Truncating audio from {len(audio_array)} to {max_samples} samples")
                    audio_array = audio_array[:max_samples]
                
                return audio_array
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            logger.error(f"Audio preprocessing failed: {e}")
            raise ValueError(f"Could not preprocess audio: {e}")
    
    def _calculate_confidence(self, result: dict) -> float:
        """Calculate confidence score from Whisper result
        
        Args:
            result: Whisper transcription result
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        try:
            # Whisper doesn't provide direct confidence scores
            # We estimate based on various factors
            
            # Check if we have segments with probability scores
            if 'segments' in result and result['segments']:
                # Average the probability scores from segments
                probs = []
                for segment in result['segments']:
                    if 'avg_logprob' in segment:
                        # Convert log probability to probability
                        prob = np.exp(segment['avg_logprob'])
                        probs.append(prob)
                
                if probs:
                    confidence = np.mean(probs)
                    # Normalize to 0-1 range (log probs are typically negative)
                    confidence = max(0.0, min(1.0, confidence))
                    return confidence
            
            # Fallback: estimate based on text characteristics
            text = result.get('text', '').strip()
            if not text:
                return 0.0
            
            # Simple heuristics for confidence estimation
            confidence = 0.7  # Base confidence
            
            # Longer text generally more reliable
            if len(text) > 20:
                confidence += 0.1
            elif len(text) < 5:
                confidence -= 0.2
            
            # Check for common transcription artifacts
            if '[' in text or ']' in text or '(' in text or ')' in text:
                confidence -= 0.1
            
            # Check for repeated words (sign of poor transcription)
            words = text.lower().split()
            if len(words) != len(set(words)) and len(words) > 2:
                confidence -= 0.1
            
            return max(0.0, min(1.0, confidence))
            
        except Exception as e:
            logger.warning(f"Could not calculate confidence: {e}")
            return 0.5  # Default moderate confidence
    
    def transcribe(self, audio_data: bytes) -> TranscriptionResult:
        """Convert audio to text with confidence scores
        
        Args:
            audio_data: Raw audio bytes
            
        Returns:
            TranscriptionResult with text and confidence
        """
        start_time = time.time()
        
        try:
            # Validate input
            if not self._validate_audio_data(audio_data):
                return TranscriptionResult(
                    text="",
                    confidence=0.0,
                    processing_time=time.time() - start_time
                )
            
            # Ensure model is loaded
            if self.model is None:
                self._load_model()
            
            # Preprocess audio
            audio_array = self._preprocess_audio(audio_data)
            
            # Transcribe with Whisper
            logger.debug("Starting Whisper transcription")
            result = self.model.transcribe(
                audio_array,
                language='en',  # Focus on English for shopping commands
                task='transcribe',
                verbose=False
            )
            
            # Extract text and calculate confidence
            text = result.get('text', '').strip()
            confidence = self._calculate_confidence(result)
            processing_time = time.time() - start_time
            
            logger.info(f"Transcription completed: '{text}' (confidence: {confidence:.2f}, time: {processing_time:.2f}s)")
            
            return TranscriptionResult(
                text=text,
                confidence=confidence,
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Transcription failed: {e}")
            
            return TranscriptionResult(
                text="",
                confidence=0.0,
                processing_time=processing_time
            )
    
    def transcribe_streaming(self, audio_stream) -> Iterator[TranscriptionResult]:
        """Real-time transcription for immediate feedback
        
        Args:
            audio_stream: Streaming audio input
            
        Yields:
            Partial transcription results
        """
        # Note: Whisper doesn't natively support streaming
        # This is a simplified implementation that processes chunks
        
        logger.warning("Streaming transcription not fully supported by Whisper - using chunked processing")
        
        chunk_size = self.sample_rate * 2  # 2 seconds of audio
        audio_buffer = bytearray()
        
        try:
            for audio_chunk in audio_stream:
                audio_buffer.extend(audio_chunk)
                
                # Process when we have enough audio
                if len(audio_buffer) >= chunk_size:
                    # Extract chunk for processing
                    chunk_data = bytes(audio_buffer[:chunk_size])
                    audio_buffer = audio_buffer[chunk_size:]
                    
                    # Transcribe chunk
                    result = self.transcribe(chunk_data)
                    
                    # Only yield if we got meaningful text
                    if result.text and result.confidence >= self.confidence_threshold:
                        yield result
            
            # Process remaining audio
            if len(audio_buffer) > 0:
                final_result = self.transcribe(bytes(audio_buffer))
                if final_result.text:
                    yield final_result
                    
        except Exception as e:
            logger.error(f"Streaming transcription failed: {e}")
            yield TranscriptionResult(text="", confidence=0.0, processing_time=0.0)
    
    def is_available(self) -> bool:
        """Check if ASR engine is available and ready"""
        return self.model is not None
    
    def get_model_info(self) -> dict:
        """Get information about the loaded model"""
        return {
            "model_size": self.model_size,
            "device": self.device,
            "confidence_threshold": self.confidence_threshold,
            "max_audio_length": self.max_audio_length,
            "sample_rate": self.sample_rate,
            "is_available": self.is_available()
        }


class ASREngineError(Exception):
    """Custom exception for ASR engine errors"""
    pass


def create_asr_engine(model_size: Optional[str] = None, device: Optional[str] = None) -> WhisperASREngine:
    """Factory function to create ASR engine instance
    
    Args:
        model_size: Whisper model size
        device: Device to run on
        
    Returns:
        Configured ASR engine instance
    """
    try:
        return WhisperASREngine(model_size=model_size, device=device)
    except Exception as e:
        logger.error(f"Failed to create ASR engine: {e}")
        raise ASREngineError(f"Could not initialize ASR engine: {e}")