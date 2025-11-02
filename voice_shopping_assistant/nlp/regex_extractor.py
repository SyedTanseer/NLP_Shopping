"""Advanced regex-based entity extraction for shopping commands"""

import re
from typing import List, Dict, Any, Optional, Tuple
from ..models.core import Entity, EntityType
from ..interfaces import EntityExtractorInterface


class RegexEntityExtractor(EntityExtractorInterface):
    """Regex-based entity extractor with comprehensive patterns"""
    
    def __init__(self):
        """Initialize regex patterns for entity extraction"""
        self._setup_patterns()
    
    def _setup_patterns(self):
        """Set up comprehensive regex patterns for different entity types"""
        
        # Price patterns with confidence scores
        self.price_patterns = [
            # Direct price formats
            (r'₹\s*(\d+(?:,\d+)*(?:\.\d{1,2})?)', 0.95),
            (r'rs\.?\s*(\d+(?:,\d+)*(?:\.\d{1,2})?)', 0.90),
            (r'rupees?\s*(\d+(?:,\d+)*(?:\.\d{1,2})?)', 0.90),
            (r'inr\s*(\d+(?:,\d+)*(?:\.\d{1,2})?)', 0.85),
            
            # Price ranges
            (r'(\d+(?:,\d+)*)\s*(?:to|-)\s*(\d+(?:,\d+)*)\s*(?:₹|rs\.?|rupees?)', 0.85),
            (r'between\s*₹?\s*(\d+(?:,\d+)*)\s*(?:and|to|-)\s*₹?\s*(\d+(?:,\d+)*)', 0.85),
            
            # Comparative prices
            (r'under\s*₹?\s*(\d+(?:,\d+)*)', 0.80),
            (r'below\s*₹?\s*(\d+(?:,\d+)*)', 0.80),
            (r'above\s*₹?\s*(\d+(?:,\d+)*)', 0.80),
            (r'over\s*₹?\s*(\d+(?:,\d+)*)', 0.80),
            (r'less\s+than\s*₹?\s*(\d+(?:,\d+)*)', 0.80),
            (r'more\s+than\s*₹?\s*(\d+(?:,\d+)*)', 0.80),
            
            # Approximate prices
            (r'around\s*₹?\s*(\d+(?:,\d+)*)', 0.70),
            (r'about\s*₹?\s*(\d+(?:,\d+)*)', 0.70),
        ]
        
        # Quantity patterns
        self.quantity_patterns = [
            # Direct numbers with units
            (r'\b(\d+)\s*(?:piece|pieces|item|items|pc|pcs)\b', 0.95),
            (r'\b(\d+)\s*(?:of\s+)?(?:the\s+)?(\w+)', 0.80),
            
            # Number words
            (r'\b(one|two|three|four|five|six|seven|eight|nine|ten)\s*(?:piece|pieces|item|items)?\b', 0.90),
            
            # Pairs and sets
            (r'\ba\s+pair\s+of\b', 0.90),  # implies 2
            (r'\ba\s+couple\s+of\b', 0.80),  # implies 2
            (r'\ba\s+few\b', 0.60),  # implies 3-5
            (r'\bseveral\b', 0.60),  # implies 3-7
            
            # Single items
            (r'\ba\s+(?!few|couple|pair)(\w+)', 0.80),  # implies 1
            (r'\bone\s+(\w+)', 0.90),
        ]
        
        # Size patterns
        self.size_patterns = [
            # Standard clothing sizes
            (r'\bsize\s*([xs|s|m|l|xl|xxl|xxxl|\d+])\b', 0.95),
            (r'\b([xs|s|m|l|xl|xxl|xxxl])\s*size\b', 0.95),
            
            # Written out sizes
            (r'\b(extra\s+small|small|medium|large|extra\s+large)\b', 0.90),
            
            # Numeric sizes
            (r'\bsize\s*(\d+(?:\.\d)?)\b', 0.90),
            (r'\b(\d+(?:\.\d)?)\s*size\b', 0.90),
            
            # Measurements
            (r'\b(\d+)\s*(?:inch|inches|"|in)\b', 0.80),
            (r'\b(\d+)\s*(?:cm|centimeter)\b', 0.80),
        ]
        
        # Brand patterns
        self.brand_patterns = [
            # Common brands
            (r'\b(nike|adidas|puma|reebok|converse|vans)\b', 0.90),
            (r'\b(zara|h&m|uniqlo|gap|forever\s*21)\b', 0.90),
            (r'\b(apple|samsung|sony|lg|dell|hp)\b', 0.90),
            
            # Brand context
            (r'\bby\s+(\w+)\b', 0.70),
            (r'\bfrom\s+(\w+)\b', 0.70),
            (r'\b(\w+)\s+brand\b', 0.80),
        ]
        
        # Material patterns
        self.material_patterns = [
            # Direct materials
            (r'\b(cotton|silk|wool|polyester|leather|denim|linen)\b', 0.85),
            
            # Material context
            (r'\bmade\s+of\s+(\w+)\b', 0.95),
            (r'\b(\w+)\s+material\b', 0.90),
            (r'\b100%\s+(\w+)\b', 0.95),
            (r'\bpure\s+(\w+)\b', 0.90),
        ]
        
        # Product patterns
        self.product_patterns = [
            # Clothing
            (r'\b(shirt|t-?shirt|tshirt|top|blouse|tank\s+top)\b', 0.85),
            (r'\b(pants|trousers|jeans|shorts|leggings)\b', 0.85),
            (r'\b(dress|skirt|gown|frock)\b', 0.85),
            (r'\b(jacket|coat|hoodie|sweater|cardigan)\b', 0.85),
            
            # Footwear
            (r'\b(shoes|sneakers|boots|sandals|heels|flats)\b', 0.85),
            
            # Accessories
            (r'\b(bag|purse|backpack|wallet|belt)\b', 0.85),
            (r'\b(watch|jewelry|necklace|earrings|ring)\b', 0.85),
            
            # Electronics
            (r'\b(phone|smartphone|laptop|tablet|computer)\b', 0.85),
            (r'\b(headphones|earbuds|speaker|camera)\b', 0.85),
        ]
        
        # Color patterns
        self.color_patterns = [
            # Basic colors
            (r'\b(red|blue|green|yellow|black|white|pink|purple|orange|brown|gray|grey)\b', 0.90),
            
            # Colors with shades
            (r'\b(light|dark|bright|pale|deep)\s+(red|blue|green|yellow|pink|purple|orange|brown|gray|grey)\b', 0.85),
            
            # Color context
            (r'\bin\s+(red|blue|green|yellow|black|white|pink|purple|orange|brown|gray|grey)\b', 0.85),
            (r'\bcolor\s+(red|blue|green|yellow|black|white|pink|purple|orange|brown|gray|grey)\b', 0.90),
        ]
    
    def extract_entities(self, text: str) -> List[Entity]:
        """Extract entities using regex patterns
        
        Args:
            text: Input text to extract entities from
            
        Returns:
            List of extracted entities
        """
        if not text or not text.strip():
            return []
        
        entities = []
        text_lower = text.lower()
        
        # Extract each entity type
        entities.extend(self._extract_price_entities(text, text_lower))
        entities.extend(self._extract_quantity_entities(text, text_lower))
        entities.extend(self._extract_size_entities(text, text_lower))
        entities.extend(self._extract_brand_entities(text, text_lower))
        entities.extend(self._extract_material_entities(text, text_lower))
        entities.extend(self._extract_product_entities(text, text_lower))
        entities.extend(self._extract_color_entities(text, text_lower))
        
        # Post-process entities
        entities = self._post_process_entities(entities)
        entities = self._remove_overlapping_entities(entities)
        
        return entities
    
    def _extract_price_entities(self, text: str, text_lower: str) -> List[Entity]:
        """Extract price entities"""
        entities = []
        
        for pattern, confidence in self.price_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                # Handle range patterns (two groups)
                if len(match.groups()) >= 2 and match.group(2):
                    value = f"{match.group(1)}-{match.group(2)}"
                else:
                    value = match.group(1) if match.groups() else match.group(0)
                
                # Clean price value
                cleaned_value = self._clean_price_value(value)
                if cleaned_value:
                    entity = Entity(
                        type=EntityType.PRICE,
                        value=cleaned_value,
                        confidence=confidence,
                        span=(match.start(), match.end())
                    )
                    entities.append(entity)
        
        return entities
    
    def _extract_quantity_entities(self, text: str, text_lower: str) -> List[Entity]:
        """Extract quantity entities"""
        entities = []
        
        for pattern, confidence in self.quantity_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                if match.groups():
                    value = match.group(1)
                else:
                    # Handle special cases
                    match_text = match.group(0)
                    if "pair" in match_text:
                        value = "2"
                    elif "couple" in match_text:
                        value = "2"
                    elif "few" in match_text:
                        value = "3"
                    else:
                        value = "1"
                
                # Convert number words
                value = self._convert_number_words(value)
                
                if self._validate_quantity(value):
                    entity = Entity(
                        type=EntityType.QUANTITY,
                        value=value,
                        confidence=confidence,
                        span=(match.start(), match.end())
                    )
                    entities.append(entity)
        
        return entities
    
    def _extract_size_entities(self, text: str, text_lower: str) -> List[Entity]:
        """Extract size entities"""
        entities = []
        
        for pattern, confidence in self.size_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                value = match.group(1) if match.groups() else match.group(0)
                
                # Normalize size
                value = self._normalize_size(value)
                
                if self._validate_size(value):
                    entity = Entity(
                        type=EntityType.SIZE,
                        value=value,
                        confidence=confidence,
                        span=(match.start(), match.end())
                    )
                    entities.append(entity)
        
        return entities
    
    def _extract_brand_entities(self, text: str, text_lower: str) -> List[Entity]:
        """Extract brand entities"""
        entities = []
        
        for pattern, confidence in self.brand_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                value = match.group(1) if match.groups() else match.group(0)
                
                # Clean brand name
                value = self._clean_brand_name(value)
                
                if len(value) >= 2:
                    entity = Entity(
                        type=EntityType.BRAND,
                        value=value,
                        confidence=confidence,
                        span=(match.start(), match.end())
                    )
                    entities.append(entity)
        
        return entities
    
    def _extract_material_entities(self, text: str, text_lower: str) -> List[Entity]:
        """Extract material entities"""
        entities = []
        
        for pattern, confidence in self.material_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                value = match.group(1) if match.groups() else match.group(0)
                
                if self._validate_material(value):
                    entity = Entity(
                        type=EntityType.MATERIAL,
                        value=value.lower(),
                        confidence=confidence,
                        span=(match.start(), match.end())
                    )
                    entities.append(entity)
        
        return entities
    
    def _extract_product_entities(self, text: str, text_lower: str) -> List[Entity]:
        """Extract product entities"""
        entities = []
        
        for pattern, confidence in self.product_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                value = match.group(1) if match.groups() else match.group(0)
                
                # Clean product name
                value = value.replace("-", "").strip()
                
                if len(value) >= 2:
                    entity = Entity(
                        type=EntityType.PRODUCT,
                        value=value.lower(),
                        confidence=confidence,
                        span=(match.start(), match.end())
                    )
                    entities.append(entity)
        
        return entities
    
    def _extract_color_entities(self, text: str, text_lower: str) -> List[Entity]:
        """Extract color entities"""
        entities = []
        
        for pattern, confidence in self.color_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                # Handle patterns with multiple groups (shade + color)
                if len(match.groups()) >= 2:
                    shade = match.group(1)
                    color = match.group(2)
                    value = f"{shade} {color}"
                else:
                    value = match.group(1) if match.groups() else match.group(0)
                
                # Normalize color
                value = self._normalize_color(value)
                
                if self._validate_color(value):
                    entity = Entity(
                        type=EntityType.COLOR,
                        value=value,
                        confidence=confidence,
                        span=(match.start(), match.end())
                    )
                    entities.append(entity)
        
        return entities
    
    def _clean_price_value(self, value: str) -> Optional[str]:
        """Clean and validate price values"""
        if not value:
            return None
        
        # Remove currency symbols and extra spaces
        cleaned = re.sub(r'[₹$rs\.rupees]', '', value, flags=re.IGNORECASE).strip()
        
        # Return cleaned numeric value
        if re.match(r'^\d+(?:,\d+)*(?:\.\d{1,2})?$', cleaned):
            return cleaned.replace(',', '')
        
        return None
    
    def _convert_number_words(self, value: str) -> str:
        """Convert number words to digits"""
        number_words = {
            "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
            "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10"
        }
        return number_words.get(value.lower(), value)
    
    def _normalize_size(self, value: str) -> str:
        """Normalize size values"""
        size_mapping = {
            "extra small": "xs",
            "small": "s",
            "medium": "m", 
            "large": "l",
            "extra large": "xl"
        }
        return size_mapping.get(value.lower(), value.lower())
    
    def _normalize_color(self, value: str) -> str:
        """Normalize color values"""
        color_mapping = {
            "grey": "gray"
        }
        return color_mapping.get(value.lower(), value.lower())
    
    def _clean_brand_name(self, value: str) -> str:
        """Clean brand names"""
        # Remove common words
        cleaned = re.sub(r'\b(by|from|brand)\b', '', value, flags=re.IGNORECASE).strip()
        return cleaned.title() if cleaned else value.title()
    
    def _validate_quantity(self, value: str) -> bool:
        """Validate quantity values"""
        if value.isdigit():
            return 1 <= int(value) <= 100
        return False
    
    def _validate_size(self, value: str) -> bool:
        """Validate size values"""
        valid_sizes = ["xs", "s", "m", "l", "xl", "xxl", "xxxl"]
        valid_sizes.extend([str(i) for i in range(6, 15)])  # Shoe sizes
        return value in valid_sizes or re.match(r'^\d+(\.\d)?$', value)
    
    def _validate_color(self, value: str) -> bool:
        """Validate color values"""
        valid_colors = [
            "red", "blue", "green", "yellow", "black", "white", "pink",
            "purple", "orange", "brown", "gray", "grey"
        ]
        
        # Check if it's a basic color or color with shade
        words = value.split()
        if len(words) == 1:
            return words[0] in valid_colors
        elif len(words) == 2:
            shade_words = ["light", "dark", "bright", "pale", "deep"]
            return words[0] in shade_words and words[1] in valid_colors
        
        return False
    
    def _validate_material(self, value: str) -> bool:
        """Validate material values"""
        valid_materials = [
            "cotton", "silk", "wool", "polyester", "leather", "denim", "linen"
        ]
        return value.lower() in valid_materials
    
    def _post_process_entities(self, entities: List[Entity]) -> List[Entity]:
        """Post-process entities for consistency"""
        processed = []
        
        for entity in entities:
            # Basic validation
            if entity.value and len(entity.value.strip()) >= 1:
                processed.append(entity)
        
        return processed
    
    def _remove_overlapping_entities(self, entities: List[Entity]) -> List[Entity]:
        """Remove overlapping entities, keeping higher confidence ones"""
        if not entities:
            return entities
        
        # Sort by start position
        sorted_entities = sorted(entities, key=lambda e: e.span[0])
        
        filtered = []
        for entity in sorted_entities:
            # Check for overlaps with existing entities
            overlaps = False
            for existing in filtered:
                if self._entities_overlap(entity, existing):
                    # Keep the one with higher confidence
                    if entity.confidence > existing.confidence:
                        filtered.remove(existing)
                        break
                    else:
                        overlaps = True
                        break
            
            if not overlaps:
                filtered.append(entity)
        
        return filtered
    
    def _entities_overlap(self, entity1: Entity, entity2: Entity) -> bool:
        """Check if two entities overlap"""
        start1, end1 = entity1.span
        start2, end2 = entity2.span
        return not (end1 <= start2 or end2 <= start1)
    
    def get_supported_entities(self) -> List[str]:
        """Get list of supported entity types"""
        return [
            EntityType.PRICE.value, EntityType.QUANTITY.value, EntityType.SIZE.value,
            EntityType.BRAND.value, EntityType.MATERIAL.value, EntityType.PRODUCT.value,
            EntityType.COLOR.value
        ]