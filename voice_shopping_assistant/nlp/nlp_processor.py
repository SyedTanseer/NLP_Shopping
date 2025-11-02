"""Complete NLP processor integrating intent classification and entity extraction"""

import time
from typing import List, Dict, Any, Optional

from ..models.core import NLPResult, Intent, Entity, EntityType, IntentType
from ..interfaces import NLPProcessorInterface
from .conversation_context import ConversationContext
from .intent_classifier import DistilBERTIntentClassifier
from .entity_extractor import create_entity_extractor
from .regex_extractor import RegexEntityExtractor
from .entity_resolver import EntityResolver


class CombinedEntityExtractor:
    """Combined entity extractor using both spaCy and regex approaches"""
    
    def __init__(self, use_spacy: bool = True):
        """Initialize combined entity extractor
        
        Args:
            use_spacy: Whether to use spaCy (falls back to regex if unavailable)
        """
        self.spacy_extractor = create_entity_extractor(use_spacy)
        self.regex_extractor = RegexEntityExtractor()
    
    def extract_entities(self, text: str) -> List[Entity]:
        """Extract entities using both approaches and combine results"""
        if not text or not text.strip():
            return []
        
        # Get entities from both extractors
        spacy_entities = []
        try:
            spacy_entities = self.spacy_extractor.extract_entities(text)
        except Exception as e:
            print(f"Warning: spaCy extraction failed: {e}")
        
        regex_entities = []
        try:
            regex_entities = self.regex_extractor.extract_entities(text)
        except Exception as e:
            print(f"Warning: Regex extraction failed: {e}")
        
        # Combine and deduplicate
        all_entities = spacy_entities + regex_entities
        final_entities = self._merge_entities(all_entities)
        
        # Sort by position
        final_entities.sort(key=lambda e: e.span[0])
        
        return final_entities
    
    def _merge_entities(self, entities: List[Entity]) -> List[Entity]:
        """Merge overlapping entities, keeping higher confidence ones"""
        if not entities:
            return entities
        
        # Group by type and span
        entity_groups = {}
        for entity in entities:
            key = (entity.type, entity.span)
            if key not in entity_groups:
                entity_groups[key] = []
            entity_groups[key].append(entity)
        
        # Keep highest confidence entity from each group
        merged = []
        for group in entity_groups.values():
            best_entity = max(group, key=lambda e: e.confidence)
            merged.append(best_entity)
        
        # Remove overlapping entities across different types
        final_entities = []
        sorted_entities = sorted(merged, key=lambda e: e.span[0])
        
        for entity in sorted_entities:
            overlaps = False
            for existing in final_entities:
                if self._entities_overlap(entity, existing):
                    if entity.confidence > existing.confidence:
                        final_entities.remove(existing)
                        break
                    else:
                        overlaps = True
                        break
            
            if not overlaps:
                final_entities.append(entity)
        
        return final_entities
    
    def _entities_overlap(self, entity1: Entity, entity2: Entity) -> bool:
        """Check if two entities overlap"""
        start1, end1 = entity1.span
        start2, end2 = entity2.span
        return not (end1 <= start2 or end2 <= start1)
    
    def get_supported_entities(self) -> List[str]:
        """Get list of all supported entity types"""
        spacy_entities = set(self.spacy_extractor.get_supported_entities())
        regex_entities = set(self.regex_extractor.get_supported_entities())
        return list(spacy_entities.union(regex_entities))


class ComprehensiveNLPProcessor(NLPProcessorInterface):
    """Complete NLP processor with intent classification, entity extraction, and resolution"""
    
    def __init__(self, intent_model_path: Optional[str] = None, use_spacy: bool = True):
        """Initialize NLP processor
        
        Args:
            intent_model_path: Path to trained intent classification model
            use_spacy: Whether to use spaCy for entity extraction
        """
        self.intent_classifier = DistilBERTIntentClassifier(intent_model_path)
        self.entity_extractor = CombinedEntityExtractor(use_spacy)
        self.entity_resolver = EntityResolver()
        
        print("NLP Processor initialized successfully")
    
    def process(self, text: str, context: ConversationContext) -> NLPResult:
        """Process text through complete NLP pipeline
        
        Args:
            text: Input text to process
            context: Conversation context for reference resolution
            
        Returns:
            Complete NLP processing result
        """
        start_time = time.time()
        
        try:
            # Step 1: Classify intent
            intent = self._classify_intent(text)
            
            # Step 2: Extract entities
            raw_entities = self._extract_entities(text)
            
            # Step 3: Resolve references and validate entities
            resolved_entities = self._resolve_entities(raw_entities, context)
            
            # Step 4: Validate entity-intent compatibility
            validated_entities = self._validate_entities(resolved_entities, intent)
            
            # Step 5: Calculate overall confidence
            confidence_score = self._calculate_confidence(intent, validated_entities)
            
            # Step 6: Update context
            self._update_context(context, text, intent, validated_entities)
            
            # Create result
            result = NLPResult(
                original_text=text,
                normalized_text=text.strip().lower(),
                intent=Intent(
                    type=intent.type,
                    confidence=intent.confidence,
                    entities=validated_entities
                ),
                entities=validated_entities,
                confidence_score=confidence_score
            )
            
            processing_time = time.time() - start_time
            print(f"NLP processing completed in {processing_time:.3f}s")
            
            return result
            
        except Exception as e:
            print(f"Error in NLP processing: {e}")
            # Return fallback result
            return self._create_fallback_result(text)
    
    def _classify_intent(self, text: str) -> Intent:
        """Classify intent from text"""
        try:
            return self.intent_classifier.classify(text)
        except Exception as e:
            print(f"Warning: Intent classification failed: {e}")
            return self._fallback_intent_classification(text)
    
    def _fallback_intent_classification(self, text: str) -> Intent:
        """Fallback rule-based intent classification"""
        text_lower = text.lower()
        
        # Simple keyword-based classification
        if any(word in text_lower for word in ["add", "buy", "purchase", "get", "want"]):
            intent_type = IntentType.ADD
            confidence = 0.7
        elif any(word in text_lower for word in ["remove", "delete", "take out", "cancel"]):
            intent_type = IntentType.REMOVE
            confidence = 0.7
        elif any(word in text_lower for word in ["search", "find", "look for", "show me"]):
            intent_type = IntentType.SEARCH
            confidence = 0.7
        elif any(word in text_lower for word in ["checkout", "pay", "order", "complete"]):
            intent_type = IntentType.CHECKOUT
            confidence = 0.7
        elif any(word in text_lower for word in ["help", "assist", "how"]):
            intent_type = IntentType.HELP
            confidence = 0.6
        else:
            intent_type = IntentType.ADD  # Default assumption
            confidence = 0.5
        
        return Intent(
            type=intent_type,
            confidence=confidence,
            entities=[]
        )
    
    def _extract_entities(self, text: str) -> List[Entity]:
        """Extract entities from text"""
        try:
            return self.entity_extractor.extract_entities(text)
        except Exception as e:
            print(f"Warning: Entity extraction failed: {e}")
            return []
    
    def _resolve_entities(self, entities: List[Entity], context: ConversationContext) -> List[Entity]:
        """Resolve entity references using context"""
        try:
            return self.entity_resolver.resolve_references(entities, context)
        except Exception as e:
            print(f"Warning: Entity resolution failed: {e}")
            return entities
    
    def _validate_entities(self, entities: List[Entity], intent: Intent) -> List[Entity]:
        """Validate entities for compatibility with intent"""
        validated = []
        
        for entity in entities:
            if self._is_entity_valid_for_intent(entity, intent.type):
                validated.append(entity)
        
        return validated
    
    def _is_entity_valid_for_intent(self, entity: Entity, intent_type: IntentType) -> bool:
        """Check if entity is valid for the given intent type"""
        
        if intent_type == IntentType.ADD:
            return entity.type in [EntityType.PRODUCT, EntityType.QUANTITY, EntityType.COLOR,
                                 EntityType.SIZE, EntityType.MATERIAL, EntityType.BRAND]
        
        elif intent_type == IntentType.REMOVE:
            return entity.type in [EntityType.PRODUCT, EntityType.COLOR, EntityType.SIZE,
                                 EntityType.QUANTITY]
        
        elif intent_type == IntentType.SEARCH:
            return entity.type in [EntityType.PRODUCT, EntityType.COLOR, EntityType.SIZE,
                                 EntityType.MATERIAL, EntityType.BRAND, EntityType.PRICE]
        
        elif intent_type == IntentType.CHECKOUT:
            return True  # CHECKOUT typically doesn't need specific entities
        
        else:
            return True  # Default: allow most entities
    
    def _calculate_confidence(self, intent: Intent, entities: List[Entity]) -> float:
        """Calculate overall confidence score"""
        
        # Start with intent confidence
        confidence = intent.confidence
        
        # Adjust based on entity quality
        if entities:
            entity_confidences = [e.confidence for e in entities]
            avg_entity_confidence = sum(entity_confidences) / len(entity_confidences)
            
            # Weighted average: 60% intent, 40% entities
            confidence = 0.6 * confidence + 0.4 * avg_entity_confidence
        else:
            # Penalize if no entities found for intents that typically need them
            if intent.type in [IntentType.ADD, IntentType.REMOVE, IntentType.SEARCH]:
                confidence *= 0.7
        
        # Check intent-entity compatibility
        if not self._check_intent_entity_compatibility(intent.type, entities):
            confidence *= 0.8
        
        return min(confidence, 1.0)
    
    def _check_intent_entity_compatibility(self, intent_type: IntentType, entities: List[Entity]) -> bool:
        """Check if entities are compatible with intent"""
        
        entity_types = {e.type for e in entities}
        
        if intent_type == IntentType.ADD:
            return EntityType.PRODUCT in entity_types
        
        elif intent_type == IntentType.REMOVE:
            return (EntityType.PRODUCT in entity_types or 
                   len(entity_types.intersection({EntityType.COLOR, EntityType.SIZE})) > 0)
        
        elif intent_type == IntentType.SEARCH:
            search_types = {EntityType.PRODUCT, EntityType.COLOR, EntityType.SIZE,
                          EntityType.MATERIAL, EntityType.BRAND, EntityType.PRICE}
            return len(entity_types.intersection(search_types)) > 0
        
        return True
    
    def _update_context(self, context: ConversationContext, text: str, 
                       intent: Intent, entities: List[Entity]):
        """Update conversation context"""
        # The context will be updated by the caller after processing is complete
        # This method is kept for interface compatibility
        pass
    
    def _create_fallback_result(self, text: str) -> NLPResult:
        """Create fallback result when processing fails"""
        fallback_intent = Intent(
            type=IntentType.HELP,
            confidence=0.3,
            entities=[]
        )
        
        return NLPResult(
            original_text=text,
            normalized_text=text.strip().lower(),
            intent=fallback_intent,
            entities=[],
            confidence_score=0.3
        )
    
    def resolve_references(self, entities: List[Entity], context: ConversationContext) -> List[Entity]:
        """Resolve pronouns like 'the red one' to specific items"""
        return self.entity_resolver.resolve_references(entities, context)
    
    def detect_ambiguity(self, entities: List[Entity], context: ConversationContext) -> List[Dict[str, Any]]:
        """Detect ambiguous entities that need clarification"""
        return self.entity_resolver.detect_ambiguity(entities, context)
    
    def validate_against_catalog(self, entities: List[Entity], product_catalog: List) -> Dict[str, Any]:
        """Validate entities against product catalog"""
        return self.entity_resolver.validate_against_catalog(entities, product_catalog)
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics and model information"""
        return {
            "intent_classifier": {
                "type": "DistilBERT",
                "supported_intents": self.intent_classifier.get_supported_intents()
            },
            "entity_extractor": {
                "type": "Combined (spaCy + Regex)",
                "supported_entities": self.entity_extractor.get_supported_entities()
            },
            "entity_resolver": {
                "type": "Context-aware resolver",
                "features": ["pronoun_resolution", "ambiguity_detection", "catalog_validation"]
            }
        }
    
    def process_batch(self, texts: List[str], contexts: List[ConversationContext]) -> List[NLPResult]:
        """Process multiple texts in batch"""
        if len(texts) != len(contexts):
            raise ValueError("Number of texts must match number of contexts")
        
        results = []
        for text, context in zip(texts, contexts):
            result = self.process(text, context)
            results.append(result)
        
        return results
    
    def get_entity_suggestions(self, partial_text: str, entity_type: EntityType) -> List[str]:
        """Get entity suggestions for autocomplete"""
        suggestions = []
        
        if entity_type == EntityType.COLOR:
            colors = ["red", "blue", "green", "yellow", "black", "white", "pink", 
                     "purple", "orange", "brown", "gray"]
            suggestions = [c for c in colors if c.startswith(partial_text.lower())]
        
        elif entity_type == EntityType.SIZE:
            sizes = ["xs", "s", "m", "l", "xl", "xxl"] + [str(i) for i in range(6, 15)]
            suggestions = [s for s in sizes if s.startswith(partial_text.lower())]
        
        elif entity_type == EntityType.MATERIAL:
            materials = ["cotton", "silk", "wool", "polyester", "leather", "denim", "linen"]
            suggestions = [m for m in materials if m.startswith(partial_text.lower())]
        
        elif entity_type == EntityType.BRAND:
            brands = ["nike", "adidas", "zara", "h&m", "apple", "samsung"]
            suggestions = [b for b in brands if b.startswith(partial_text.lower())]
        
        return suggestions[:5]  # Return top 5 suggestions


# Factory function for easy instantiation
def create_nlp_processor(intent_model_path: Optional[str] = None, 
                        use_spacy: bool = True) -> NLPProcessorInterface:
    """Create NLP processor instance
    
    Args:
        intent_model_path: Path to trained intent model
        use_spacy: Whether to use spaCy for entity extraction
        
    Returns:
        NLP processor instance
    """
    return ComprehensiveNLPProcessor(intent_model_path, use_spacy)