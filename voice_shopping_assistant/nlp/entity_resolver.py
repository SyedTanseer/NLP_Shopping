"""Entity resolution system for handling pronouns, ambiguity, and validation"""

import re
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum

from ..models.core import Entity, EntityType, Product, CartItem, CartSummary, IntentType
from .conversation_context import ConversationContext, CommandRecord


class ReferenceType(Enum):
    """Types of references that need resolution"""
    PRONOUN = "pronoun"           # it, that, this, them
    DEMONSTRATIVE = "demonstrative"  # the red one, the first one
    ORDINAL = "ordinal"           # the first, the second, the last
    COMPARATIVE = "comparative"    # the cheaper one, the larger one
    CONTEXTUAL = "contextual"     # same, another, different


@dataclass
class Reference:
    """A reference that needs to be resolved"""
    text: str
    type: ReferenceType
    span: Tuple[int, int]
    confidence: float
    context_clues: List[str]


@dataclass
class ResolutionCandidate:
    """A candidate for resolving a reference"""
    entity: Entity
    score: float
    reason: str
    source: str  # 'cart', 'history', 'context'


class EntityResolver:
    """Resolves entity references using conversation context and cart state"""
    
    def __init__(self):
        """Initialize entity resolver"""
        self._setup_reference_patterns()
        self._setup_validation_rules()
    
    def _setup_reference_patterns(self):
        """Set up patterns for detecting references"""
        
        # Pronoun patterns
        self.pronoun_patterns = [
            (r'\b(it|that|this)\b', ReferenceType.PRONOUN, 0.9),
            (r'\b(them|those|these)\b', ReferenceType.PRONOUN, 0.85),
        ]
        
        # Demonstrative patterns
        self.demonstrative_patterns = [
            (r'\bthe\s+(\w+)\s+one\b', ReferenceType.DEMONSTRATIVE, 0.8),
            (r'\bthat\s+(\w+)\s+one\b', ReferenceType.DEMONSTRATIVE, 0.85),
        ]
        
        # Ordinal patterns
        self.ordinal_patterns = [
            (r'\bthe\s+(first|second|third|last)\s+one\b', ReferenceType.ORDINAL, 0.9),
            (r'\bthe\s+(first|second|third|last)\b', ReferenceType.ORDINAL, 0.85),
        ]
        
        # Comparative patterns
        self.comparative_patterns = [
            (r'\bthe\s+(cheaper|expensive|larger|smaller)\s+one\b', ReferenceType.COMPARATIVE, 0.8),
            (r'\bthe\s+(cheapest|most\s+expensive|largest|smallest)\b', ReferenceType.COMPARATIVE, 0.85),
        ]
        
        # Contextual patterns
        self.contextual_patterns = [
            (r'\b(same|similar)\b', ReferenceType.CONTEXTUAL, 0.7),
            (r'\b(another|different)\b', ReferenceType.CONTEXTUAL, 0.75),
        ]
    
    def _setup_validation_rules(self):
        """Set up validation rules for entity combinations"""
        
        # Compatible entity combinations
        self.compatible_combinations = {
            EntityType.PRODUCT: [EntityType.COLOR, EntityType.SIZE, EntityType.MATERIAL, 
                               EntityType.BRAND, EntityType.QUANTITY],
            EntityType.COLOR: [EntityType.PRODUCT, EntityType.SIZE, EntityType.MATERIAL],
            EntityType.SIZE: [EntityType.PRODUCT, EntityType.COLOR, EntityType.MATERIAL],
            EntityType.MATERIAL: [EntityType.PRODUCT, EntityType.COLOR, EntityType.SIZE],
            EntityType.BRAND: [EntityType.PRODUCT],
            EntityType.QUANTITY: [EntityType.PRODUCT],
            EntityType.PRICE: [EntityType.PRODUCT]
        }
    
    def resolve_references(self, entities: List[Entity], context: ConversationContext) -> List[Entity]:
        """Resolve pronoun and contextual references in entities
        
        Args:
            entities: List of extracted entities
            context: Conversation context with history and cart state
            
        Returns:
            List of entities with references resolved
        """
        if not entities:
            return entities
        
        # Detect references in the entities
        references = self._detect_references(entities)
        
        if not references:
            return entities
        
        # Resolve each reference
        resolved_entities = []
        for entity in entities:
            if self._is_reference_entity(entity, references):
                # Try to resolve this reference
                resolved = self._resolve_reference(entity, references, context)
                if resolved:
                    resolved_entities.extend(resolved)
                else:
                    # Keep original if can't resolve
                    resolved_entities.append(entity)
            else:
                resolved_entities.append(entity)
        
        return resolved_entities
    
    def detect_ambiguity(self, entities: List[Entity], context: ConversationContext) -> List[Dict[str, Any]]:
        """Detect ambiguous entities that need clarification
        
        Args:
            entities: List of extracted entities
            context: Conversation context
            
        Returns:
            List of ambiguity issues with suggested clarifications
        """
        ambiguities = []
        
        # Check for missing required entities
        missing = self._check_missing_entities(entities)
        if missing:
            ambiguities.append({
                "type": "missing_entities",
                "missing": missing,
                "message": f"Please specify {', '.join(missing)}",
                "severity": "high"
            })
        
        # Check for conflicting entities
        conflicts = self._check_entity_conflicts(entities)
        if conflicts:
            ambiguities.append({
                "type": "conflicting_entities",
                "conflicts": conflicts,
                "message": "Multiple conflicting values detected",
                "severity": "high"
            })
        
        # Check for vague references
        vague_refs = self._check_vague_references(entities, context)
        if vague_refs:
            ambiguities.append({
                "type": "vague_references",
                "references": vague_refs,
                "message": "Some references are unclear",
                "severity": "medium"
            })
        
        # Check for incomplete specifications
        incomplete = self._check_incomplete_specifications(entities)
        if incomplete:
            ambiguities.append({
                "type": "incomplete_specification",
                "missing_details": incomplete,
                "message": "Product specification is incomplete",
                "severity": "low"
            })
        
        return ambiguities
    
    def validate_against_catalog(self, entities: List[Entity], product_catalog: List[Product]) -> Dict[str, Any]:
        """Validate entities against product catalog
        
        Args:
            entities: List of extracted entities
            product_catalog: Available products
            
        Returns:
            Validation result with matches and suggestions
        """
        validation_result = {
            "valid": True,
            "matches": [],
            "suggestions": [],
            "issues": []
        }
        
        # Build product specification from entities
        product_spec = self._build_product_specification(entities)
        
        if not product_spec.get("product"):
            validation_result["issues"].append("No product specified")
            validation_result["valid"] = False
            return validation_result
        
        # Find matching products
        matches = self._find_matching_products(product_spec, product_catalog)
        validation_result["matches"] = matches
        
        if not matches:
            validation_result["valid"] = False
            validation_result["issues"].append("No matching products found")
            
            # Generate suggestions
            suggestions = self._generate_suggestions(product_spec, product_catalog)
            validation_result["suggestions"] = suggestions
        else:
            # Validate specific attributes
            attribute_validation = self._validate_attributes(product_spec, matches)
            validation_result.update(attribute_validation)
        
        return validation_result
    
    def _detect_references(self, entities: List[Entity]) -> List[Reference]:
        """Detect references in entities"""
        references = []
        
        for entity in entities:
            text = entity.value.lower()
            
            # Check all pattern types
            all_patterns = (self.pronoun_patterns + self.demonstrative_patterns + 
                          self.ordinal_patterns + self.comparative_patterns + 
                          self.contextual_patterns)
            
            for pattern, ref_type, confidence in all_patterns:
                match = re.search(pattern, text)
                if match:
                    context_clues = []
                    if match.groups():
                        context_clues = [g for g in match.groups() if g]
                    
                    reference = Reference(
                        text=match.group(0),
                        type=ref_type,
                        span=entity.span,
                        confidence=confidence,
                        context_clues=context_clues
                    )
                    references.append(reference)
        
        return references
    
    def _is_reference_entity(self, entity: Entity, references: List[Reference]) -> bool:
        """Check if an entity contains a reference"""
        for ref in references:
            if (entity.span[0] <= ref.span[0] <= entity.span[1] or
                entity.span[0] <= ref.span[1] <= entity.span[1]):
                return True
        return False
    
    def _resolve_reference(self, entity: Entity, references: List[Reference], 
                          context: ConversationContext) -> Optional[List[Entity]]:
        """Resolve a specific reference entity"""
        
        # Find applicable reference
        applicable_ref = None
        for ref in references:
            if (entity.span[0] <= ref.span[0] <= entity.span[1] or
                entity.span[0] <= ref.span[1] <= entity.span[1]):
                applicable_ref = ref
                break
        
        if not applicable_ref:
            return None
        
        # Get resolution candidates
        candidates = self._get_resolution_candidates(applicable_ref, context)
        
        if not candidates:
            return None
        
        # Score and rank candidates
        scored_candidates = self._score_candidates(applicable_ref, candidates)
        
        # Return best candidate if confidence is high enough
        if scored_candidates and scored_candidates[0].score >= 0.6:
            return [scored_candidates[0].entity]
        
        return None
    
    def _get_resolution_candidates(self, reference: Reference, 
                                 context: ConversationContext) -> List[ResolutionCandidate]:
        """Get candidates for resolving a reference"""
        candidates = []
        
        # Get candidates from cart
        if context.cart_state and context.cart_state.items:
            cart_candidates = self._get_cart_candidates(reference, context.cart_state)
            candidates.extend(cart_candidates)
        
        # Get candidates from history
        if context.command_history:
            history_candidates = self._get_history_candidates(reference, context)
            candidates.extend(history_candidates)
        
        return candidates
    
    def _get_cart_candidates(self, reference: Reference, 
                           cart_state: CartSummary) -> List[ResolutionCandidate]:
        """Get resolution candidates from cart items"""
        candidates = []
        
        for i, cart_item in enumerate(cart_state.items):
            product = cart_item.product
            
            # Calculate score based on reference type and context
            score = self._calculate_cart_score(reference, cart_item, i)
            
            # Create product entity candidate
            product_entity = Entity(
                type=EntityType.PRODUCT,
                value=product.name,
                confidence=0.9,
                span=(0, len(product.name))
            )
            
            candidate = ResolutionCandidate(
                entity=product_entity,
                score=score,
                reason=f"Cart item {i+1}: {product.name}",
                source="cart"
            )
            candidates.append(candidate)
            
            # Add attribute entities if available
            if cart_item.color:
                color_entity = Entity(
                    type=EntityType.COLOR,
                    value=cart_item.color,
                    confidence=0.9,
                    span=(0, len(cart_item.color))
                )
                candidates.append(ResolutionCandidate(
                    entity=color_entity,
                    score=score * 0.8,
                    reason=f"Color from cart: {cart_item.color}",
                    source="cart"
                ))
            
            if cart_item.size:
                size_entity = Entity(
                    type=EntityType.SIZE,
                    value=cart_item.size,
                    confidence=0.9,
                    span=(0, len(cart_item.size))
                )
                candidates.append(ResolutionCandidate(
                    entity=size_entity,
                    score=score * 0.8,
                    reason=f"Size from cart: {cart_item.size}",
                    source="cart"
                ))
        
        return candidates
    
    def _get_history_candidates(self, reference: Reference, 
                              context: ConversationContext) -> List[ResolutionCandidate]:
        """Get resolution candidates from conversation history"""
        candidates = []
        
        # Get recent commands for better context
        recent_commands = context.get_recent_commands(5)
        
        for i, command in enumerate(reversed(recent_commands)):
            # Score based on recency and success
            recency_score = 1.0 - (i * 0.15)
            success_boost = 1.2 if command.success else 0.8
            
            for entity in command.entities:
                relevance_score = self._calculate_history_relevance(reference, entity)
                score = recency_score * relevance_score * success_boost
                
                if score > 0.3:
                    candidate = ResolutionCandidate(
                        entity=entity,
                        score=score,
                        reason=f"From command: '{command.original_text[:30]}...'",
                        source="history"
                    )
                    candidates.append(candidate)
        
        return candidates
    
    def _calculate_cart_score(self, reference: Reference, cart_item: CartItem, position: int) -> float:
        """Calculate score for a cart item candidate"""
        base_score = 0.7
        
        # Boost for ordinal references
        if reference.type == ReferenceType.ORDINAL:
            ordinal_map = {"first": 0, "second": 1, "third": 2, "last": -1}
            for ordinal in reference.context_clues:
                if ordinal in ordinal_map:
                    expected_pos = ordinal_map[ordinal]
                    if expected_pos == -1:  # "last"
                        expected_pos = len(cart_item.product.name) - 1
                    if position == expected_pos:
                        base_score += 0.3
                    break
        
        # Boost for matching context clues
        for clue in reference.context_clues:
            if clue.lower() in cart_item.product.name.lower():
                base_score += 0.2
            if cart_item.color and clue.lower() == cart_item.color.lower():
                base_score += 0.2
            if cart_item.size and clue.lower() == cart_item.size.lower():
                base_score += 0.2
        
        return min(base_score, 1.0)
    
    def _calculate_history_relevance(self, reference: Reference, entity: Entity) -> float:
        """Calculate relevance score for a history entity"""
        base_score = 0.5
        
        # Boost for matching context clues
        for clue in reference.context_clues:
            if clue.lower() in entity.value.lower():
                base_score += 0.3
        
        # Boost for relevant entity types
        if reference.type == ReferenceType.DEMONSTRATIVE:
            if entity.type in [EntityType.PRODUCT, EntityType.COLOR]:
                base_score += 0.2
        
        return min(base_score, 1.0)
    
    def _score_candidates(self, reference: Reference, 
                         candidates: List[ResolutionCandidate]) -> List[ResolutionCandidate]:
        """Score and rank resolution candidates"""
        
        for candidate in candidates:
            # Boost cart items (more relevant)
            if candidate.source == "cart":
                candidate.score *= 1.2
            
            # Apply reference confidence
            candidate.score *= reference.confidence
        
        # Sort by score (highest first)
        return sorted(candidates, key=lambda c: c.score, reverse=True)
    
    def _check_missing_entities(self, entities: List[Entity]) -> List[str]:
        """Check for missing required entities"""
        entity_types = {entity.type for entity in entities}
        missing = []
        
        # For shopping commands, typically need product and quantity
        if EntityType.PRODUCT not in entity_types:
            missing.append("product type")
        
        if EntityType.QUANTITY not in entity_types:
            missing.append("quantity")
        
        return missing
    
    def _check_entity_conflicts(self, entities: List[Entity]) -> List[Dict[str, Any]]:
        """Check for conflicting entity values"""
        conflicts = []
        type_counts = {}
        
        # Count entities by type
        for entity in entities:
            if entity.type not in type_counts:
                type_counts[entity.type] = []
            type_counts[entity.type].append(entity)
        
        # Check for conflicts (multiple values of same type)
        conflicting_types = [EntityType.COLOR, EntityType.SIZE, EntityType.MATERIAL, EntityType.BRAND]
        
        for entity_type, entity_list in type_counts.items():
            if len(entity_list) > 1 and entity_type in conflicting_types:
                values = [e.value for e in entity_list]
                conflicts.append({
                    "type": entity_type.value,
                    "values": values,
                    "message": f"Multiple {entity_type.value} values: {', '.join(values)}"
                })
        
        return conflicts
    
    def _check_vague_references(self, entities: List[Entity], 
                               context: ConversationContext) -> List[str]:
        """Check for vague references that couldn't be resolved"""
        vague_refs = []
        
        for entity in entities:
            if entity.value.lower() in ["it", "that", "this", "them", "those", "these"]:
                # Check if we have context to resolve
                if not context.cart_state or not context.cart_state.items:
                    vague_refs.append(entity.value)
        
        return vague_refs
    
    def _check_incomplete_specifications(self, entities: List[Entity]) -> List[str]:
        """Check for incomplete product specifications"""
        entity_types = {entity.type for entity in entities}
        incomplete = []
        
        # If we have a product, check for common missing attributes
        if EntityType.PRODUCT in entity_types:
            product_entities = [e for e in entities if e.type == EntityType.PRODUCT]
            for product_entity in product_entities:
                if self._is_clothing_item(product_entity.value):
                    if EntityType.SIZE not in entity_types:
                        incomplete.append("size")
                    if EntityType.COLOR not in entity_types:
                        incomplete.append("color preference")
        
        return incomplete
    
    def _is_clothing_item(self, product_name: str) -> bool:
        """Check if a product is a clothing item"""
        clothing_keywords = [
            "shirt", "pants", "dress", "jacket", "sweater", "jeans",
            "shorts", "skirt", "blouse", "hoodie", "coat", "top"
        ]
        return any(keyword in product_name.lower() for keyword in clothing_keywords)
    
    def _build_product_specification(self, entities: List[Entity]) -> Dict[str, Any]:
        """Build product specification from entities"""
        spec = {}
        
        for entity in entities:
            if entity.type == EntityType.PRODUCT:
                spec["product"] = entity.value
            elif entity.type == EntityType.COLOR:
                spec["color"] = entity.value
            elif entity.type == EntityType.SIZE:
                spec["size"] = entity.value
            elif entity.type == EntityType.MATERIAL:
                spec["material"] = entity.value
            elif entity.type == EntityType.BRAND:
                spec["brand"] = entity.value
            elif entity.type == EntityType.QUANTITY:
                spec["quantity"] = entity.value
            elif entity.type == EntityType.PRICE:
                spec["price"] = entity.value
        
        return spec
    
    def _find_matching_products(self, product_spec: Dict[str, Any], 
                               product_catalog: List[Product]) -> List[Product]:
        """Find products matching the specification"""
        matches = []
        
        for product in product_catalog:
            if self._product_matches_spec(product, product_spec):
                matches.append(product)
        
        return matches
    
    def _product_matches_spec(self, product: Product, spec: Dict[str, Any]) -> bool:
        """Check if a product matches the specification"""
        
        # Check product name/category
        if "product" in spec:
            product_name = spec["product"].lower()
            if (product_name not in product.name.lower() and 
                product_name not in product.category.lower()):
                return False
        
        # Check color availability
        if "color" in spec:
            if not product.is_available_in_color(spec["color"]):
                return False
        
        # Check size availability
        if "size" in spec:
            if not product.is_available_in_size(spec["size"]):
                return False
        
        # Check material
        if "material" in spec:
            if spec["material"].lower() not in product.material.lower():
                return False
        
        # Check brand
        if "brand" in spec:
            if spec["brand"].lower() not in product.brand.lower():
                return False
        
        return True
    
    def _validate_attributes(self, spec: Dict[str, Any], matches: List[Product]) -> Dict[str, Any]:
        """Validate product attributes against matches"""
        validation = {
            "attribute_issues": [],
            "attribute_suggestions": []
        }
        
        if not matches:
            return validation
        
        # Check color availability
        if "color" in spec:
            available_colors = set()
            for product in matches:
                available_colors.update(product.available_colors)
            
            if spec["color"] not in available_colors:
                validation["attribute_issues"].append(f"Color '{spec['color']}' not available")
                validation["attribute_suggestions"].append({
                    "attribute": "color",
                    "available": list(available_colors)
                })
        
        # Check size availability
        if "size" in spec:
            available_sizes = set()
            for product in matches:
                available_sizes.update(product.available_sizes)
            
            if spec["size"] not in available_sizes:
                validation["attribute_issues"].append(f"Size '{spec['size']}' not available")
                validation["attribute_suggestions"].append({
                    "attribute": "size",
                    "available": list(available_sizes)
                })
        
        return validation
    
    def _generate_suggestions(self, spec: Dict[str, Any], 
                            product_catalog: List[Product]) -> List[Dict[str, Any]]:
        """Generate product suggestions when no exact matches found"""
        suggestions = []
        
        if "product" in spec:
            product_name = spec["product"].lower()
            similar_products = []
            
            for product in product_catalog:
                # Simple similarity based on common words
                product_words = set(product.name.lower().split())
                spec_words = set(product_name.split())
                
                common_words = product_words.intersection(spec_words)
                if common_words:
                    similarity = len(common_words) / max(len(product_words), len(spec_words))
                    if similarity > 0.3:
                        similar_products.append((product, similarity))
            
            # Sort by similarity and take top 3
            similar_products.sort(key=lambda x: x[1], reverse=True)
            
            for product, similarity in similar_products[:3]:
                suggestions.append({
                    "type": "similar_product",
                    "product": product.to_dict(),
                    "similarity": similarity,
                    "reason": "Similar product name"
                })
        
        return suggestions
    
    def resolve_cross_command_references(self, entities: List[Entity], 
                                       context: ConversationContext) -> List[Entity]:
        """Resolve references that span multiple commands"""
        resolved_entities = []
        
        for entity in entities:
            if self._is_cross_command_reference(entity):
                resolved = self._resolve_cross_command_reference(entity, context)
                if resolved:
                    resolved_entities.extend(resolved)
                else:
                    resolved_entities.append(entity)
            else:
                resolved_entities.append(entity)
        
        return resolved_entities
    
    def _is_cross_command_reference(self, entity: Entity) -> bool:
        """Check if entity is a cross-command reference"""
        cross_command_phrases = [
            "same as before", "like last time", "the previous one",
            "what I ordered", "my usual", "the same thing"
        ]
        
        return any(phrase in entity.value.lower() for phrase in cross_command_phrases)
    
    def _resolve_cross_command_reference(self, entity: Entity, 
                                       context: ConversationContext) -> Optional[List[Entity]]:
        """Resolve cross-command references"""
        
        # Look for successful ADD commands in history
        add_commands = context.get_commands_by_intent(IntentType.ADD, 3)
        
        if not add_commands:
            return None
        
        # Get entities from the most recent successful ADD command
        last_successful_add = None
        for command in add_commands:
            if command.success:
                last_successful_add = command
                break
        
        if not last_successful_add:
            return None
        
        # Return product-related entities from that command
        relevant_entities = []
        for hist_entity in last_successful_add.entities:
            if hist_entity.type in [EntityType.PRODUCT, EntityType.COLOR, 
                                  EntityType.SIZE, EntityType.MATERIAL, EntityType.BRAND]:
                # Create new entity with updated confidence
                new_entity = Entity(
                    type=hist_entity.type,
                    value=hist_entity.value,
                    confidence=hist_entity.confidence * 0.9,  # Slightly lower confidence
                    span=entity.span  # Use current span
                )
                relevant_entities.append(new_entity)
        
        return relevant_entities if relevant_entities else None
    
    def resolve_comparative_references(self, entities: List[Entity], 
                                     context: ConversationContext) -> List[Entity]:
        """Resolve comparative references like 'cheaper one', 'larger size'"""
        resolved_entities = []
        
        for entity in entities:
            if self._is_comparative_reference(entity):
                resolved = self._resolve_comparative_reference(entity, context)
                if resolved:
                    resolved_entities.extend(resolved)
                else:
                    resolved_entities.append(entity)
            else:
                resolved_entities.append(entity)
        
        return resolved_entities
    
    def _is_comparative_reference(self, entity: Entity) -> bool:
        """Check if entity is a comparative reference"""
        comparative_words = [
            "cheaper", "expensive", "larger", "smaller", "bigger", "better",
            "different", "alternative", "other", "another"
        ]
        
        return any(word in entity.value.lower() for word in comparative_words)
    
    def _resolve_comparative_reference(self, entity: Entity, 
                                     context: ConversationContext) -> Optional[List[Entity]]:
        """Resolve comparative references using cart and history"""
        
        # Get comparison base from cart or recent searches
        comparison_base = self._get_comparison_base(context)
        
        if not comparison_base:
            return None
        
        # Extract comparison criteria
        criteria = self._extract_comparison_criteria(entity.value)
        
        if not criteria:
            return None
        
        # Generate resolved entity based on criteria
        resolved_entity = self._apply_comparison_criteria(criteria, comparison_base, entity)
        
        return [resolved_entity] if resolved_entity else None
    
    def _get_comparison_base(self, context: ConversationContext) -> Optional[Dict[str, Any]]:
        """Get base item for comparison from context"""
        
        # First try cart items
        if context.cart_state and context.cart_state.items:
            last_item = context.cart_state.items[-1]
            return {
                "product": last_item.product.name,
                "price": last_item.product.price,
                "color": last_item.color,
                "size": last_item.size,
                "source": "cart"
            }
        
        # Then try recent search results from history
        recent_commands = context.get_recent_commands(3)
        for command in recent_commands:
            if command.intent.type == IntentType.SEARCH and command.success:
                product_entities = [e for e in command.entities if e.type == EntityType.PRODUCT]
                if product_entities:
                    return {
                        "product": product_entities[0].value,
                        "source": "search_history"
                    }
        
        return None
    
    def _extract_comparison_criteria(self, text: str) -> Optional[Dict[str, str]]:
        """Extract comparison criteria from text"""
        text_lower = text.lower()
        
        criteria = {}
        
        # Price comparisons
        if "cheaper" in text_lower or "less expensive" in text_lower:
            criteria["price"] = "lower"
        elif "expensive" in text_lower or "pricier" in text_lower:
            criteria["price"] = "higher"
        
        # Size comparisons
        if "larger" in text_lower or "bigger" in text_lower:
            criteria["size"] = "larger"
        elif "smaller" in text_lower:
            criteria["size"] = "smaller"
        
        # Alternative/different
        if "different" in text_lower or "alternative" in text_lower or "other" in text_lower:
            criteria["type"] = "alternative"
        
        return criteria if criteria else None
    
    def _apply_comparison_criteria(self, criteria: Dict[str, str], 
                                 base: Dict[str, Any], 
                                 original_entity: Entity) -> Optional[Entity]:
        """Apply comparison criteria to generate resolved entity"""
        
        # For now, create a modified entity with comparison context
        # In a full implementation, this would query the product catalog
        
        resolved_value = original_entity.value
        
        if "price" in criteria:
            if criteria["price"] == "lower":
                resolved_value = f"cheaper {base.get('product', 'item')}"
            else:
                resolved_value = f"more expensive {base.get('product', 'item')}"
        
        elif "size" in criteria:
            if criteria["size"] == "larger":
                resolved_value = f"larger size of {base.get('product', 'item')}"
            else:
                resolved_value = f"smaller size of {base.get('product', 'item')}"
        
        elif criteria.get("type") == "alternative":
            resolved_value = f"alternative to {base.get('product', 'item')}"
        
        return Entity(
            type=EntityType.PRODUCT,
            value=resolved_value,
            confidence=original_entity.confidence * 0.8,
            span=original_entity.span
        )
    
    def link_entities_across_commands(self, entities: List[Entity], 
                                    context: ConversationContext) -> Dict[str, Any]:
        """Link entities across multiple commands for better understanding"""
        
        entity_links = {
            "current_entities": entities,
            "linked_entities": [],
            "context_entities": [],
            "confidence_boost": {}
        }
        
        # Get recent entities for linking
        recent_entities = context.get_recent_entities(count=15)
        
        for current_entity in entities:
            # Find related entities in history
            related_entities = self._find_related_entities(current_entity, recent_entities)
            
            if related_entities:
                entity_links["linked_entities"].append({
                    "current": current_entity.to_dict(),
                    "related": [e.to_dict() for e in related_entities],
                    "link_strength": self._calculate_link_strength(current_entity, related_entities)
                })
                
                # Boost confidence if we have strong links
                if len(related_entities) >= 2:
                    entity_links["confidence_boost"][current_entity.value] = 0.1
        
        # Add contextual entities that might be relevant
        contextual_entities = self._get_contextual_entities(entities, context)
        entity_links["context_entities"] = [e.to_dict() for e in contextual_entities]
        
        return entity_links
    
    def _find_related_entities(self, target_entity: Entity, 
                             history_entities: List[Entity]) -> List[Entity]:
        """Find entities related to the target entity"""
        related = []
        
        for hist_entity in history_entities:
            if self._are_entities_related(target_entity, hist_entity):
                related.append(hist_entity)
        
        return related
    
    def _are_entities_related(self, entity1: Entity, entity2: Entity) -> bool:
        """Check if two entities are related"""
        
        # Same type and similar values
        if entity1.type == entity2.type:
            return self._calculate_text_similarity(entity1.value, entity2.value) > 0.7
        
        # Compatible types (e.g., product and color)
        if entity1.type in self.compatible_combinations.get(entity2.type, []):
            return True
        
        if entity2.type in self.compatible_combinations.get(entity1.type, []):
            return True
        
        return False
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def _calculate_link_strength(self, current_entity: Entity, 
                               related_entities: List[Entity]) -> float:
        """Calculate strength of entity links"""
        if not related_entities:
            return 0.0
        
        total_strength = 0.0
        for related in related_entities:
            # Base strength from entity relationship
            if current_entity.type == related.type:
                strength = 0.8
            elif current_entity.type in self.compatible_combinations.get(related.type, []):
                strength = 0.6
            else:
                strength = 0.3
            
            # Boost for high confidence entities
            if related.confidence > 0.8:
                strength *= 1.2
            
            total_strength += strength
        
        return min(total_strength / len(related_entities), 1.0)
    
    def _get_contextual_entities(self, current_entities: List[Entity], 
                               context: ConversationContext) -> List[Entity]:
        """Get contextual entities that might be relevant"""
        contextual = []
        
        # If we have a product but missing common attributes, suggest from history
        current_types = {e.type for e in current_entities}
        
        if EntityType.PRODUCT in current_types:
            # Look for recent color/size mentions if missing
            if EntityType.COLOR not in current_types:
                recent_colors = context.get_recent_entities(EntityType.COLOR, 3)
                if recent_colors:
                    contextual.extend(recent_colors[:1])  # Add most recent color
            
            if EntityType.SIZE not in current_types:
                recent_sizes = context.get_recent_entities(EntityType.SIZE, 3)
                if recent_sizes:
                    contextual.extend(recent_sizes[:1])  # Add most recent size
        
        return contextual