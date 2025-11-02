"""Entity extraction using spaCy NER for shopping commands"""

import re
from typing import List, Dict, Any, Optional, Tuple
from abc import ABC, abstractmethod

try:
    import spacy
    from spacy.tokens import Doc
    from spacy.matcher import Matcher
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    # Create dummy Doc class for type hints when spaCy is not available
    class Doc:
        pass
    print("Warning: spaCy not available. Using fallback entity extraction.")

from ..models.core import Entity, EntityType
from ..interfaces import EntityExtractorInterface


class BaseEntityExtractor(EntityExtractorInterface):
    """Base class for entity extractors"""
    
    def __init__(self):
        self.supported_entities = [
            EntityType.PRODUCT, EntityType.COLOR, EntityType.SIZE,
            EntityType.MATERIAL, EntityType.QUANTITY, EntityType.PRICE, EntityType.BRAND
        ]
    
    def get_supported_entities(self) -> List[str]:
        """Get list of supported entity types"""
        return [entity_type.value for entity_type in self.supported_entities]


class SpacyEntityExtractor(BaseEntityExtractor):
    """spaCy-based entity extractor with custom patterns for shopping"""
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        """Initialize spaCy NER pipeline
        
        Args:
            model_name: spaCy model to use for NER
        """
        super().__init__()
        self.model_name = model_name
        self.nlp = None
        self.matcher = None
        
        if SPACY_AVAILABLE:
            self._load_spacy_model()
            self._setup_custom_patterns()
        else:
            print("spaCy not available, using fallback patterns")
    
    def _load_spacy_model(self):
        """Load spaCy model with fallback options"""
        try:
            self.nlp = spacy.load(self.model_name)
            print(f"Loaded spaCy model: {self.model_name}")
        except OSError:
            try:
                # Try loading a smaller model
                self.nlp = spacy.load("en_core_web_sm")
                print("Loaded fallback spaCy model: en_core_web_sm")
            except OSError:
                # Create blank model as last resort
                from spacy.lang.en import English
                self.nlp = English()
                print("Using blank English spaCy model")
        
        # Initialize matcher
        if self.nlp:
            self.matcher = Matcher(self.nlp.vocab)
    
    def _setup_custom_patterns(self):
        """Set up custom patterns for shopping entities"""
        if not self.matcher:
            return
        
        # Product patterns
        product_patterns = [
            [{"LOWER": {"IN": ["shirt", "t-shirt", "tshirt", "top", "blouse"]}}],
            [{"LOWER": {"IN": ["pants", "trousers", "jeans", "shorts"]}}],
            [{"LOWER": {"IN": ["dress", "skirt", "gown"]}}],
            [{"LOWER": {"IN": ["shoes", "sneakers", "boots", "sandals"]}}],
            [{"LOWER": {"IN": ["jacket", "coat", "hoodie", "sweater"]}}],
            [{"LOWER": {"IN": ["bag", "purse", "backpack", "wallet"]}}],
            [{"LOWER": {"IN": ["phone", "laptop", "tablet", "headphones"]}}],
        ]
        
        # Color patterns
        color_patterns = [
            [{"LOWER": {"IN": ["red", "blue", "green", "yellow", "black", "white", 
                              "pink", "purple", "orange", "brown", "gray", "grey"]}}],
        ]
        
        # Size patterns
        size_patterns = [
            [{"LOWER": {"IN": ["xs", "s", "m", "l", "xl", "xxl"]}}],
            [{"LOWER": "size"}, {"IS_DIGIT": True}],
            [{"LOWER": {"IN": ["small", "medium", "large"]}}],
        ]
        
        # Material patterns
        material_patterns = [
            [{"LOWER": {"IN": ["cotton", "silk", "wool", "polyester", "leather", "denim"]}}],
        ]
        
        # Quantity patterns
        quantity_patterns = [
            [{"IS_DIGIT": True}],
            [{"LOWER": {"IN": ["one", "two", "three", "four", "five"]}}],
        ]
        
        # Add patterns to matcher
        try:
            self.matcher.add("PRODUCT", product_patterns)
            self.matcher.add("COLOR", color_patterns)
            self.matcher.add("SIZE", size_patterns)
            self.matcher.add("MATERIAL", material_patterns)
            self.matcher.add("QUANTITY", quantity_patterns)
        except Exception as e:
            print(f"Warning: Error setting up spaCy patterns: {e}")
    
    def extract_entities(self, text: str) -> List[Entity]:
        """Extract entities from text using spaCy NER
        
        Args:
            text: Input text to extract entities from
            
        Returns:
            List of extracted entities
        """
        if not text or not text.strip():
            return []
        
        entities = []
        
        if self.nlp and SPACY_AVAILABLE:
            try:
                # Process text with spaCy
                doc = self.nlp(text)
                
                # Extract using custom patterns
                if self.matcher:
                    pattern_entities = self._extract_pattern_entities(doc)
                    entities.extend(pattern_entities)
                
                # Extract using built-in NER
                spacy_entities = self._extract_spacy_entities(doc)
                entities.extend(spacy_entities)
                
            except Exception as e:
                print(f"Warning: spaCy extraction failed: {e}")
                # Fall back to simple pattern matching
                entities = self._fallback_extraction(text)
        else:
            # Use fallback extraction
            entities = self._fallback_extraction(text)
        
        # Post-process and validate
        entities = self._post_process_entities(entities, text)
        entities = self._remove_duplicates(entities)
        
        return entities
    
    def _extract_pattern_entities(self, doc: Doc) -> List[Entity]:
        """Extract entities using custom patterns"""
        entities = []
        
        try:
            matches = self.matcher(doc)
            
            for match_id, start, end in matches:
                label = self.nlp.vocab.strings[match_id]
                span = doc[start:end]
                
                # Map pattern labels to EntityType
                entity_type_map = {
                    "PRODUCT": EntityType.PRODUCT,
                    "COLOR": EntityType.COLOR,
                    "SIZE": EntityType.SIZE,
                    "MATERIAL": EntityType.MATERIAL,
                    "QUANTITY": EntityType.QUANTITY
                }
                
                if label in entity_type_map:
                    entity = Entity(
                        type=entity_type_map[label],
                        value=span.text.strip(),
                        confidence=0.85,
                        span=(span.start_char, span.end_char)
                    )
                    entities.append(entity)
        
        except Exception as e:
            print(f"Warning: Pattern extraction failed: {e}")
        
        return entities
    
    def _extract_spacy_entities(self, doc: Doc) -> List[Entity]:
        """Extract entities using spaCy's built-in NER"""
        entities = []
        
        try:
            for ent in doc.ents:
                entity_type = self._map_spacy_label(ent.label_)
                
                if entity_type:
                    confidence = self._calculate_confidence(ent)
                    
                    entity = Entity(
                        type=entity_type,
                        value=ent.text.strip(),
                        confidence=confidence,
                        span=(ent.start_char, ent.end_char)
                    )
                    entities.append(entity)
        
        except Exception as e:
            print(f"Warning: spaCy NER extraction failed: {e}")
        
        return entities
    
    def _map_spacy_label(self, spacy_label: str) -> Optional[EntityType]:
        """Map spaCy entity labels to our EntityType"""
        label_mapping = {
            "ORG": EntityType.BRAND,
            "MONEY": EntityType.PRICE,
            "CARDINAL": EntityType.QUANTITY,
            "ORDINAL": EntityType.QUANTITY,
        }
        return label_mapping.get(spacy_label)
    
    def _calculate_confidence(self, ent) -> float:
        """Calculate confidence for spaCy entities"""
        base_confidence = 0.7
        
        # Adjust based on entity type
        type_confidence = {
            "MONEY": 0.9,
            "CARDINAL": 0.8,
            "ORG": 0.75
        }
        
        return type_confidence.get(ent.label_, base_confidence)
    
    def _fallback_extraction(self, text: str) -> List[Entity]:
        """Fallback extraction using simple patterns"""
        entities = []
        text_lower = text.lower()
        
        # Simple product detection
        products = ["shirt", "pants", "dress", "shoes", "jacket", "bag"]
        for product in products:
            if product in text_lower:
                start = text_lower.find(product)
                entity = Entity(
                    type=EntityType.PRODUCT,
                    value=product,
                    confidence=0.6,
                    span=(start, start + len(product))
                )
                entities.append(entity)
        
        # Simple color detection
        colors = ["red", "blue", "green", "black", "white", "yellow"]
        for color in colors:
            if color in text_lower:
                start = text_lower.find(color)
                entity = Entity(
                    type=EntityType.COLOR,
                    value=color,
                    confidence=0.7,
                    span=(start, start + len(color))
                )
                entities.append(entity)
        
        # Simple quantity detection
        import re
        quantity_pattern = r'\b(\d+)\b'
        for match in re.finditer(quantity_pattern, text):
            entity = Entity(
                type=EntityType.QUANTITY,
                value=match.group(1),
                confidence=0.8,
                span=(match.start(), match.end())
            )
            entities.append(entity)
        
        return entities
    
    def _post_process_entities(self, entities: List[Entity], text: str) -> List[Entity]:
        """Post-process and validate entities"""
        processed = []
        
        for entity in entities:
            # Normalize values
            normalized_value = self._normalize_value(entity.value, entity.type)
            
            # Validate
            if self._validate_entity(normalized_value, entity.type):
                processed_entity = Entity(
                    type=entity.type,
                    value=normalized_value,
                    confidence=entity.confidence,
                    span=entity.span
                )
                processed.append(processed_entity)
        
        return processed
    
    def _normalize_value(self, value: str, entity_type: EntityType) -> str:
        """Normalize entity values"""
        value = value.strip().lower()
        
        if entity_type == EntityType.SIZE:
            size_mapping = {
                "extra small": "xs",
                "small": "s", 
                "medium": "m",
                "large": "l",
                "extra large": "xl"
            }
            return size_mapping.get(value, value)
        
        elif entity_type == EntityType.QUANTITY:
            number_words = {
                "one": "1", "two": "2", "three": "3", 
                "four": "4", "five": "5"
            }
            return number_words.get(value, value)
        
        return value
    
    def _validate_entity(self, value: str, entity_type: EntityType) -> bool:
        """Validate entity values"""
        if entity_type == EntityType.QUANTITY:
            if value.isdigit():
                return 1 <= int(value) <= 100
            return False
        
        elif entity_type == EntityType.SIZE:
            valid_sizes = ["xs", "s", "m", "l", "xl", "xxl"]
            valid_sizes.extend([str(i) for i in range(6, 15)])
            return value in valid_sizes
        
        elif entity_type == EntityType.COLOR:
            valid_colors = [
                "red", "blue", "green", "yellow", "black", "white",
                "pink", "purple", "orange", "brown", "gray", "grey"
            ]
            return value in valid_colors
        
        return len(value) >= 2  # Basic validation for other types
    
    def _remove_duplicates(self, entities: List[Entity]) -> List[Entity]:
        """Remove duplicate entities"""
        seen = set()
        unique_entities = []
        
        for entity in entities:
            key = (entity.type, entity.value, entity.span)
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)
        
        return unique_entities


class FallbackEntityExtractor(BaseEntityExtractor):
    """Fallback entity extractor when spaCy is not available"""
    
    def __init__(self):
        super().__init__()
        self._setup_patterns()
    
    def _setup_patterns(self):
        """Set up regex patterns for entity extraction"""
        self.patterns = {
            EntityType.PRODUCT: [
                r'\b(shirt|t-?shirt|top|blouse)\b',
                r'\b(pants|trousers|jeans|shorts)\b',
                r'\b(dress|skirt|gown)\b',
                r'\b(shoes|sneakers|boots|sandals)\b',
                r'\b(jacket|coat|hoodie|sweater)\b',
                r'\b(bag|purse|backpack|wallet)\b',
            ],
            EntityType.COLOR: [
                r'\b(red|blue|green|yellow|black|white|pink|purple|orange|brown|gray|grey)\b'
            ],
            EntityType.SIZE: [
                r'\bsize\s*([xs|s|m|l|xl|xxl|\d+])\b',
                r'\b([xs|s|m|l|xl|xxl])\s*size\b',
                r'\b(small|medium|large)\b'
            ],
            EntityType.QUANTITY: [
                r'\b(\d+)\s*(?:piece|pieces|item|items)?\b',
                r'\b(one|two|three|four|five|six|seven|eight|nine|ten)\b'
            ],
            EntityType.PRICE: [
                r'₹\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
                r'rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
                r'under\s*₹?\s*(\d+(?:,\d+)*)'
            ]
        }
    
    def extract_entities(self, text: str) -> List[Entity]:
        """Extract entities using regex patterns"""
        if not text or not text.strip():
            return []
        
        entities = []
        text_lower = text.lower()
        
        for entity_type, patterns in self.patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    value = match.group(1) if match.groups() else match.group(0)
                    
                    entity = Entity(
                        type=entity_type,
                        value=value.strip(),
                        confidence=0.7,
                        span=(match.start(), match.end())
                    )
                    entities.append(entity)
        
        return self._post_process_entities(entities)
    
    def _post_process_entities(self, entities: List[Entity]) -> List[Entity]:
        """Post-process entities"""
        processed = []
        
        for entity in entities:
            # Basic validation
            if len(entity.value) >= 1:
                processed.append(entity)
        
        return processed


# Factory function to create appropriate extractor
def create_entity_extractor(use_spacy: bool = True) -> EntityExtractorInterface:
    """Create entity extractor based on availability
    
    Args:
        use_spacy: Whether to try using spaCy (falls back if not available)
        
    Returns:
        Entity extractor instance
    """
    if use_spacy and SPACY_AVAILABLE:
        return SpacyEntityExtractor()
    else:
        return FallbackEntityExtractor()