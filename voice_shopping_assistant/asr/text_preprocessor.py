"""Text preprocessing pipeline for ASR output"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from ..interfaces import TextPreprocessorInterface


logger = logging.getLogger(__name__)


class TextPreprocessor(TextPreprocessorInterface):
    """Text preprocessing for voice shopping commands"""
    
    def __init__(self):
        """Initialize text preprocessor with patterns and mappings"""
        self._setup_currency_patterns()
        self._setup_number_mappings()
        self._setup_filler_words()
        self._setup_normalization_patterns()
    
    def _setup_currency_patterns(self) -> None:
        """Setup currency normalization patterns"""
        self.currency_patterns = [
            # Rupee symbol and variations
            (r'₹\s*(\d+)', r'INR \1'),
            (r'rs\.?\s*(\d+)', r'INR \1'),
            (r'rupees?\s*(\d+)', r'INR \1'),
            (r'(\d+)\s*rupees?', r'INR \1'),
            (r'(\d+)\s*rs\.?', r'INR \1'),
            (r'(\d+)\s*₹', r'INR \1'),
            
            # Dollar variations
            (r'\$\s*(\d+)', r'USD \1'),
            (r'dollars?\s*(\d+)', r'USD \1'),
            (r'(\d+)\s*dollars?', r'USD \1'),
            (r'(\d+)\s*\$', r'USD \1'),
            
            # Generic price patterns
            (r'price\s+of\s+(\d+)', r'price INR \1'),
            (r'costs?\s+(\d+)', r'costs INR \1'),
            (r'worth\s+(\d+)', r'worth INR \1'),
        ]
    
    def _setup_number_mappings(self) -> None:
        """Setup number word to digit mappings"""
        self.number_words = {
            # Basic numbers
            'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4',
            'five': '5', 'six': '6', 'seven': '7', 'eight': '8', 'nine': '9',
            'ten': '10', 'eleven': '11', 'twelve': '12', 'thirteen': '13',
            'fourteen': '14', 'fifteen': '15', 'sixteen': '16', 'seventeen': '17',
            'eighteen': '18', 'nineteen': '19', 'twenty': '20', 'thirty': '30',
            'forty': '40', 'fifty': '50', 'sixty': '60', 'seventy': '70',
            'eighty': '80', 'ninety': '90',
            
            # Hundreds and thousands
            'hundred': '100', 'thousand': '1000',
            
            # Common shopping quantities
            'a': '1', 'an': '1', 'single': '1', 'double': '2', 'triple': '3',
            'pair': '2', 'couple': '2', 'few': '3', 'several': '5',
            'half': '0.5', 'quarter': '0.25',
        }
        
        # Complex number patterns
        self.number_patterns = [
            # Twenty-one, thirty-two, etc.
            (r'twenty[- ]?one', '21'), (r'twenty[- ]?two', '22'), (r'twenty[- ]?three', '23'),
            (r'twenty[- ]?four', '24'), (r'twenty[- ]?five', '25'), (r'twenty[- ]?six', '26'),
            (r'twenty[- ]?seven', '27'), (r'twenty[- ]?eight', '28'), (r'twenty[- ]?nine', '29'),
            
            (r'thirty[- ]?one', '31'), (r'thirty[- ]?two', '32'), (r'thirty[- ]?three', '33'),
            (r'thirty[- ]?four', '34'), (r'thirty[- ]?five', '35'), (r'thirty[- ]?six', '36'),
            (r'thirty[- ]?seven', '37'), (r'thirty[- ]?eight', '38'), (r'thirty[- ]?nine', '39'),
            
            # Hundreds with numbers
            (r'(\w+)\s+hundred\s+(\w+)', self._convert_hundred_pattern),
            (r'(\w+)\s+hundred', self._convert_simple_hundred),
            
            # Thousands
            (r'(\w+)\s+thousand', self._convert_thousand_pattern),
        ]
    
    def _setup_filler_words(self) -> None:
        """Setup filler words to remove"""
        self.filler_words = {
            'um', 'uh', 'er', 'ah', 'like', 'you know', 'i mean', 'actually',
            'basically', 'literally', 'totally', 'really', 'very', 'quite',
            'sort of', 'kind of', 'i guess', 'i think', 'maybe', 'perhaps',
            'well', 'so', 'anyway', 'ok', 'okay', 'right', 'yeah', 'yes',
            'no problem', 'sure', 'of course', 'definitely'
        }
        
        # Patterns for removing hesitations and repetitions
        self.filler_patterns = [
            r'\b(um+|uh+|er+|ah+)\b',  # Hesitation sounds
            r'\b(\w+)\s+\1\b',  # Repeated words (e.g., "the the")
            r'\b(and|or|but)\s+(and|or|but)\b',  # Repeated conjunctions
        ]
    
    def _setup_normalization_patterns(self) -> None:
        """Setup general text normalization patterns"""
        self.normalization_patterns = [
            # Multiple spaces to single space
            (r'\s+', ' '),
            
            # Remove extra punctuation
            (r'[.]{2,}', '.'),
            (r'[!]{2,}', '!'),
            (r'[?]{2,}', '?'),
            
            # Normalize contractions
            (r"won't", "will not"),
            (r"can't", "cannot"),
            (r"n't", " not"),
            (r"'re", " are"),
            (r"'ve", " have"),
            (r"'ll", " will"),
            (r"'d", " would"),
            (r"'m", " am"),
            
            # Shopping-specific normalizations
            (r'\bsize\s+(\w+)', r'size \1'),
            (r'\bcolor\s+(\w+)', r'color \1'),
            (r'\bcolour\s+(\w+)', r'color \1'),  # British to American spelling
            (r'\bmaterial\s+(\w+)', r'material \1'),
            (r'\bbrand\s+(\w+)', r'brand \1'),
        ]
    
    def _convert_hundred_pattern(self, match) -> str:
        """Convert 'number hundred number' pattern"""
        try:
            first_num = self.number_words.get(match.group(1).lower(), match.group(1))
            second_num = self.number_words.get(match.group(2).lower(), match.group(2))
            
            if first_num.isdigit() and second_num.isdigit():
                result = int(first_num) * 100 + int(second_num)
                return str(result)
        except (ValueError, AttributeError):
            pass
        
        return match.group(0)  # Return original if conversion fails
    
    def _convert_simple_hundred(self, match) -> str:
        """Convert 'number hundred' pattern"""
        try:
            num = self.number_words.get(match.group(1).lower(), match.group(1))
            if num.isdigit():
                result = int(num) * 100
                return str(result)
        except (ValueError, AttributeError):
            pass
        
        return match.group(0)
    
    def _convert_thousand_pattern(self, match) -> str:
        """Convert 'number thousand' pattern"""
        try:
            num = self.number_words.get(match.group(1).lower(), match.group(1))
            if num.isdigit():
                result = int(num) * 1000
                return str(result)
        except (ValueError, AttributeError):
            pass
        
        return match.group(0)
    
    def normalize_currency(self, text: str) -> str:
        """Normalize currency expressions
        
        Args:
            text: Input text with currency expressions
            
        Returns:
            Text with normalized currency format
        """
        normalized = text.lower()
        
        # Apply currency patterns
        for pattern, replacement in self.currency_patterns:
            normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
        
        logger.debug(f"Currency normalization: '{text}' -> '{normalized}'")
        return normalized
    
    def normalize_numbers(self, text: str) -> str:
        """Convert number words to digits
        
        Args:
            text: Input text with number words
            
        Returns:
            Text with numbers converted to digits
        """
        normalized = text.lower()
        
        # Apply complex number patterns first
        for pattern, replacement in self.number_patterns:
            if callable(replacement):
                normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
            else:
                normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
        
        # Apply simple word-to-number mappings
        words = normalized.split()
        converted_words = []
        
        for word in words:
            # Remove punctuation for matching
            clean_word = re.sub(r'[^\w]', '', word.lower())
            if clean_word in self.number_words:
                # Preserve original punctuation
                punctuation = re.sub(r'[\w]', '', word)
                converted_words.append(self.number_words[clean_word] + punctuation)
            else:
                converted_words.append(word)
        
        result = ' '.join(converted_words)
        logger.debug(f"Number normalization: '{text}' -> '{result}'")
        return result
    
    def remove_filler_words(self, text: str) -> str:
        """Remove filler words and hesitations
        
        Args:
            text: Input text with filler words
            
        Returns:
            Text with filler words removed
        """
        cleaned = text.lower()
        
        # Remove filler patterns
        for pattern in self.filler_patterns:
            cleaned = re.sub(pattern, ' ', cleaned, flags=re.IGNORECASE)
        
        # Remove individual filler words
        words = cleaned.split()
        filtered_words = []
        
        i = 0
        while i < len(words):
            word = words[i].strip('.,!?')
            
            # Check for multi-word fillers
            if i < len(words) - 1:
                two_word = f"{word} {words[i+1].strip('.,!?')}"
                if two_word in self.filler_words:
                    i += 2  # Skip both words
                    continue
            
            # Check single word fillers
            if word not in self.filler_words:
                filtered_words.append(words[i])
            
            i += 1
        
        result = ' '.join(filtered_words)
        logger.debug(f"Filler removal: '{text}' -> '{result}'")
        return result
    
    def apply_general_normalization(self, text: str) -> str:
        """Apply general text normalization
        
        Args:
            text: Input text
            
        Returns:
            Normalized text
        """
        normalized = text
        
        # Apply normalization patterns
        for pattern, replacement in self.normalization_patterns:
            normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)
        
        # Clean up whitespace
        normalized = normalized.strip()
        
        logger.debug(f"General normalization: '{text}' -> '{normalized}'")
        return normalized
    
    def normalize_text(self, text: str) -> str:
        """Normalize text for NLP processing
        
        Args:
            text: Raw transcribed text
            
        Returns:
            Normalized text ready for NLP
        """
        if not text or not text.strip():
            return ""
        
        logger.debug(f"Starting text normalization: '{text}'")
        
        # Apply normalization steps in order
        normalized = text
        
        # 1. General normalization (contractions, spacing, etc.)
        normalized = self.apply_general_normalization(normalized)
        
        # 2. Remove filler words
        normalized = self.remove_filler_words(normalized)
        
        # 3. Normalize numbers
        normalized = self.normalize_numbers(normalized)
        
        # 4. Normalize currency
        normalized = self.normalize_currency(normalized)
        
        # 5. Final cleanup
        normalized = self.apply_general_normalization(normalized)
        
        logger.info(f"Text normalization complete: '{text}' -> '{normalized}'")
        return normalized
    
    def get_preprocessing_stats(self, original: str, normalized: str) -> Dict[str, any]:
        """Get statistics about the preprocessing
        
        Args:
            original: Original text
            normalized: Normalized text
            
        Returns:
            Dictionary with preprocessing statistics
        """
        return {
            "original_length": len(original),
            "normalized_length": len(normalized),
            "original_words": len(original.split()),
            "normalized_words": len(normalized.split()),
            "reduction_ratio": 1 - (len(normalized) / len(original)) if original else 0,
            "has_currency": any(pattern in normalized.lower() for pattern in ['inr', 'usd', '₹', '$']),
            "has_numbers": any(char.isdigit() for char in normalized),
        }


def create_text_preprocessor() -> TextPreprocessor:
    """Factory function to create text preprocessor instance
    
    Returns:
        Configured text preprocessor instance
    """
    return TextPreprocessor()