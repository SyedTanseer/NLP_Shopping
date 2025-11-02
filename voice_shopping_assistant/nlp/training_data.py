"""Training data preparation utilities for intent classification"""

import json
import csv
import random
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set
from dataclasses import dataclass, asdict
import logging
from collections import Counter, defaultdict

from ..models.core import IntentType


logger = logging.getLogger(__name__)


@dataclass
class TrainingExample:
    """Single training example for intent classification"""
    text: str
    intent: IntentType
    confidence: float = 1.0
    source: str = "manual"
    
    def to_dict(self) -> Dict[str, any]:
        """Convert to dictionary for serialization"""
        return {
            "text": self.text,
            "intent": self.intent.value,
            "confidence": self.confidence,
            "source": self.source
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, any]) -> 'TrainingExample':
        """Create from dictionary"""
        return cls(
            text=data["text"],
            intent=IntentType(data["intent"]),
            confidence=data.get("confidence", 1.0),
            source=data.get("source", "manual")
        )


class TrainingDataGenerator:
    """Generate and augment training data for shopping intent classification"""
    
    def __init__(self):
        """Initialize training data generator"""
        self.base_templates = self._create_base_templates()
        self.product_names = self._get_product_names()
        self.colors = self._get_colors()
        self.sizes = self._get_sizes()
        self.quantities = self._get_quantities()
        self.materials = self._get_materials()
        self.brands = self._get_brands()
        self.price_ranges = self._get_price_ranges()
        
    def _create_base_templates(self) -> Dict[IntentType, List[str]]:
        """Create base templates for each intent type"""
        return {
            IntentType.ADD: [
                "add {quantity} {color} {product} to my cart",
                "I want {quantity} {product} in {color}",
                "put {quantity} {size} {product} in my cart",
                "I need {quantity} {product}",
                "add {product} to cart",
                "get me {quantity} {color} {product}",
                "I want to buy {quantity} {product}",
                "add {quantity} {material} {product}",
                "put {quantity} {brand} {product} in my cart",
                "I need {quantity} {size} {color} {product}",
                "add {product}",
                "I want {product}",
                "get {product}",
                "buy {quantity} {product}",
                "purchase {product}",
                "I'll take {quantity} {product}",
                "add {quantity} of {product}",
                "put {product} in my cart",
                "I want to add {product}",
                "include {quantity} {product}"
            ],
            IntentType.REMOVE: [
                "remove {product} from my cart",
                "delete {product}",
                "take out {product}",
                "I don't want {product} anymore",
                "remove {quantity} {product}",
                "cancel {product}",
                "delete {quantity} {color} {product}",
                "take away {product}",
                "remove the {color} {product}",
                "I changed my mind about {product}",
                "don't want {product}",
                "eliminate {product}",
                "remove all {product}",
                "take out the {size} {product}",
                "cancel {quantity} {product}",
                "delete the {brand} {product}",
                "remove {product} from cart",
                "I don't need {product}",
                "take away {quantity} {product}",
                "remove that {product}"
            ],
            IntentType.SEARCH: [
                "search for {product}",
                "find {color} {product}",
                "show me {product}",
                "do you have {product}",
                "look for {size} {product}",
                "what {product} do you have",
                "find {material} {product}",
                "search {brand} {product}",
                "show {color} {product}",
                "I'm looking for {product}",
                "find me {product}",
                "what {color} {product} are available",
                "search for {size} {product}",
                "do you sell {product}",
                "show me {price_range} {product}",
                "find {product} under {price_range}",
                "look for cheap {product}",
                "search expensive {product}",
                "what {brand} {product} do you have",
                "browse {product}"
            ],
            IntentType.CHECKOUT: [
                "checkout",
                "proceed to checkout",
                "I want to pay",
                "complete my order",
                "finish shopping",
                "pay now",
                "place order",
                "buy now",
                "proceed to payment",
                "I'm ready to pay",
                "complete purchase",
                "finalize order",
                "go to checkout",
                "I want to buy everything",
                "purchase all items",
                "pay for my cart",
                "complete my purchase",
                "I'm done shopping",
                "ready to checkout",
                "process payment"
            ],
            IntentType.HELP: [
                "help",
                "what can you do",
                "how does this work",
                "what are my options",
                "help me",
                "I need assistance",
                "what commands can I use",
                "how to add items",
                "how to remove items",
                "what can I say",
                "guide me",
                "instructions",
                "how to search",
                "how to checkout",
                "what features do you have",
                "show me commands",
                "I'm confused",
                "I need help",
                "assist me",
                "support"
            ],
            IntentType.CANCEL: [
                "cancel",
                "stop",
                "quit",
                "exit",
                "never mind",
                "forget it",
                "abort",
                "end session",
                "I'm done",
                "cancel everything",
                "stop shopping",
                "quit shopping",
                "end",
                "cancel order",
                "abort shopping",
                "I don't want anything",
                "clear everything",
                "start over",
                "reset",
                "cancel all"
            ]
        }
    
    def _get_product_names(self) -> List[str]:
        """Get list of common product names"""
        return [
            "shirt", "t-shirt", "jeans", "pants", "dress", "skirt", "jacket", "coat",
            "shoes", "sneakers", "boots", "sandals", "hat", "cap", "scarf", "gloves",
            "sweater", "hoodie", "shorts", "socks", "underwear", "bra", "belt", "bag",
            "backpack", "purse", "wallet", "watch", "sunglasses", "jewelry", "ring",
            "necklace", "earrings", "bracelet", "phone", "laptop", "tablet", "headphones",
            "charger", "case", "book", "notebook", "pen", "pencil", "water bottle",
            "coffee mug", "plate", "bowl", "cup", "spoon", "fork", "knife"
        ]
    
    def _get_colors(self) -> List[str]:
        """Get list of common colors"""
        return [
            "red", "blue", "green", "yellow", "black", "white", "gray", "grey",
            "brown", "pink", "purple", "orange", "navy", "maroon", "beige", "tan",
            "gold", "silver", "dark blue", "light blue", "dark green", "light green",
            "bright red", "deep red", "pale yellow", "bright yellow"
        ]
    
    def _get_sizes(self) -> List[str]:
        """Get list of common sizes"""
        return [
            "small", "medium", "large", "extra large", "xs", "s", "m", "l", "xl", "xxl",
            "size 6", "size 7", "size 8", "size 9", "size 10", "size 11", "size 12",
            "32", "34", "36", "38", "40", "42", "44"
        ]
    
    def _get_quantities(self) -> List[str]:
        """Get list of quantity expressions"""
        return [
            "1", "2", "3", "4", "5", "one", "two", "three", "four", "five",
            "a", "an", "a pair of", "some", "several", "a few", "multiple"
        ]
    
    def _get_materials(self) -> List[str]:
        """Get list of common materials"""
        return [
            "cotton", "silk", "wool", "leather", "denim", "polyester", "linen",
            "cashmere", "velvet", "satin", "canvas", "suede", "plastic", "metal",
            "wooden", "glass", "ceramic", "rubber"
        ]
    
    def _get_brands(self) -> List[str]:
        """Get list of common brand names (generic)"""
        return [
            "nike", "adidas", "puma", "reebok", "converse", "vans", "zara", "h&m",
            "uniqlo", "gap", "levis", "calvin klein", "tommy hilfiger", "polo",
            "gucci", "prada", "versace", "armani", "boss", "diesel"
        ]
    
    def _get_price_ranges(self) -> List[str]:
        """Get list of price range expressions"""
        return [
            "under 100", "under 500", "under 1000", "under 50", "cheap", "expensive",
            "budget", "premium", "affordable", "high-end", "low-cost", "mid-range",
            "below 200", "above 500", "between 100 and 500"
        ]
    
    def generate_training_examples(self, num_examples_per_intent: int = 100) -> List[TrainingExample]:
        """Generate training examples for all intents
        
        Args:
            num_examples_per_intent: Number of examples to generate per intent
            
        Returns:
            List of training examples
        """
        examples = []
        
        for intent_type in IntentType:
            intent_examples = self._generate_intent_examples(intent_type, num_examples_per_intent)
            examples.extend(intent_examples)
        
        # Shuffle examples
        random.shuffle(examples)
        
        logger.info(f"Generated {len(examples)} training examples")
        return examples
    
    def _generate_intent_examples(self, intent_type: IntentType, num_examples: int) -> List[TrainingExample]:
        """Generate examples for a specific intent
        
        Args:
            intent_type: Intent to generate examples for
            num_examples: Number of examples to generate
            
        Returns:
            List of training examples for the intent
        """
        examples = []
        templates = self.base_templates.get(intent_type, [])
        
        if not templates:
            logger.warning(f"No templates found for intent {intent_type}")
            return examples
        
        for _ in range(num_examples):
            template = random.choice(templates)
            
            # Fill template with random values
            filled_text = self._fill_template(template)
            
            # Apply variations
            varied_text = self._apply_variations(filled_text)
            
            example = TrainingExample(
                text=varied_text,
                intent=intent_type,
                confidence=1.0,
                source="generated"
            )
            examples.append(example)
        
        return examples
    
    def _fill_template(self, template: str) -> str:
        """Fill template placeholders with random values
        
        Args:
            template: Template string with placeholders
            
        Returns:
            Filled template string
        """
        text = template
        
        # Replace placeholders
        if "{product}" in text:
            text = text.replace("{product}", random.choice(self.product_names))
        if "{color}" in text:
            text = text.replace("{color}", random.choice(self.colors))
        if "{size}" in text:
            text = text.replace("{size}", random.choice(self.sizes))
        if "{quantity}" in text:
            text = text.replace("{quantity}", random.choice(self.quantities))
        if "{material}" in text:
            text = text.replace("{material}", random.choice(self.materials))
        if "{brand}" in text:
            text = text.replace("{brand}", random.choice(self.brands))
        if "{price_range}" in text:
            text = text.replace("{price_range}", random.choice(self.price_ranges))
        
        return text
    
    def _apply_variations(self, text: str) -> str:
        """Apply random variations to text
        
        Args:
            text: Input text
            
        Returns:
            Text with applied variations
        """
        variations = [
            self._add_filler_words,
            self._add_politeness,
            self._change_capitalization,
            self._add_punctuation_variations,
            self._add_speech_patterns
        ]
        
        # Apply 1-3 random variations
        num_variations = random.randint(1, 3)
        selected_variations = random.sample(variations, num_variations)
        
        for variation_func in selected_variations:
            text = variation_func(text)
        
        return text.strip()
    
    def _add_filler_words(self, text: str) -> str:
        """Add filler words to make text more natural"""
        fillers = ["um", "uh", "well", "so", "like", "you know", "actually", "basically"]
        
        if random.random() < 0.3:  # 30% chance to add filler
            filler = random.choice(fillers)
            if random.random() < 0.5:
                text = f"{filler} {text}"
            else:
                words = text.split()
                if len(words) > 2:
                    insert_pos = random.randint(1, len(words) - 1)
                    words.insert(insert_pos, filler)
                    text = " ".join(words)
        
        return text
    
    def _add_politeness(self, text: str) -> str:
        """Add polite expressions"""
        polite_starts = ["please", "could you", "can you", "would you mind"]
        polite_ends = ["please", "thank you", "thanks"]
        
        if random.random() < 0.2:  # 20% chance to add politeness
            if random.random() < 0.5:
                polite = random.choice(polite_starts)
                text = f"{polite} {text}"
            else:
                polite = random.choice(polite_ends)
                text = f"{text} {polite}"
        
        return text
    
    def _change_capitalization(self, text: str) -> str:
        """Apply random capitalization patterns"""
        patterns = [
            lambda x: x.lower(),
            lambda x: x.upper(),
            lambda x: x.capitalize(),
            lambda x: x.title(),
            lambda x: x  # no change
        ]
        
        pattern = random.choice(patterns)
        return pattern(text)
    
    def _add_punctuation_variations(self, text: str) -> str:
        """Add punctuation variations"""
        if random.random() < 0.3:  # 30% chance to modify punctuation
            endings = [".", "!", "?", ""]
            text = text.rstrip(".,!?") + random.choice(endings)
        
        return text
    
    def _add_speech_patterns(self, text: str) -> str:
        """Add common speech patterns"""
        patterns = [
            ("I want", ["I'd like", "I need", "I'm looking for", "Can I get"]),
            ("add", ["put", "include", "get me"]),
            ("remove", ["delete", "take out", "get rid of"]),
            ("search", ["find", "look for", "show me"])
        ]
        
        for original, replacements in patterns:
            if original in text.lower() and random.random() < 0.2:
                replacement = random.choice(replacements)
                text = re.sub(re.escape(original), replacement, text, flags=re.IGNORECASE)
                break
        
        return text


class TrainingDataManager:
    """Manage training data loading, validation, and quality checks"""
    
    def __init__(self):
        """Initialize training data manager"""
        self.generator = TrainingDataGenerator()
    
    def load_from_file(self, file_path: str) -> List[TrainingExample]:
        """Load training data from file
        
        Args:
            file_path: Path to training data file (JSON or CSV)
            
        Returns:
            List of training examples
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Training data file not found: {file_path}")
        
        if file_path.suffix.lower() == '.json':
            return self._load_from_json(file_path)
        elif file_path.suffix.lower() == '.csv':
            return self._load_from_csv(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    def _load_from_json(self, file_path: Path) -> List[TrainingExample]:
        """Load training data from JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        examples = []
        for item in data:
            try:
                example = TrainingExample.from_dict(item)
                examples.append(example)
            except Exception as e:
                logger.warning(f"Skipping invalid training example: {e}")
        
        logger.info(f"Loaded {len(examples)} examples from {file_path}")
        return examples
    
    def _load_from_csv(self, file_path: Path) -> List[TrainingExample]:
        """Load training data from CSV file"""
        examples = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                try:
                    example = TrainingExample(
                        text=row['text'],
                        intent=IntentType(row['intent']),
                        confidence=float(row.get('confidence', 1.0)),
                        source=row.get('source', 'manual')
                    )
                    examples.append(example)
                except Exception as e:
                    logger.warning(f"Skipping invalid CSV row: {e}")
        
        logger.info(f"Loaded {len(examples)} examples from {file_path}")
        return examples
    
    def save_to_file(self, examples: List[TrainingExample], file_path: str) -> None:
        """Save training data to file
        
        Args:
            examples: List of training examples
            file_path: Output file path (JSON or CSV)
        """
        file_path = Path(file_path)
        
        # Create directory if it doesn't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        if file_path.suffix.lower() == '.json':
            self._save_to_json(examples, file_path)
        elif file_path.suffix.lower() == '.csv':
            self._save_to_csv(examples, file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    def _save_to_json(self, examples: List[TrainingExample], file_path: Path) -> None:
        """Save training data to JSON file"""
        data = [example.to_dict() for example in examples]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(examples)} examples to {file_path}")
    
    def _save_to_csv(self, examples: List[TrainingExample], file_path: Path) -> None:
        """Save training data to CSV file"""
        if not examples:
            return
        
        fieldnames = ['text', 'intent', 'confidence', 'source']
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for example in examples:
                writer.writerow(example.to_dict())
        
        logger.info(f"Saved {len(examples)} examples to {file_path}")
    
    def validate_training_data(self, examples: List[TrainingExample]) -> Dict[str, any]:
        """Validate training data quality and distribution
        
        Args:
            examples: List of training examples
            
        Returns:
            Validation report dictionary
        """
        if not examples:
            return {"valid": False, "error": "No training examples provided"}
        
        # Count examples per intent
        intent_counts = Counter(example.intent for example in examples)
        
        # Check for minimum examples per intent
        min_examples = 10
        insufficient_intents = [intent for intent, count in intent_counts.items() if count < min_examples]
        
        # Check for text duplicates
        text_counts = Counter(example.text.lower().strip() for example in examples)
        duplicates = [text for text, count in text_counts.items() if count > 1]
        
        # Check text length distribution
        text_lengths = [len(example.text.split()) for example in examples]
        avg_length = sum(text_lengths) / len(text_lengths)
        
        # Check confidence distribution
        confidences = [example.confidence for example in examples]
        avg_confidence = sum(confidences) / len(confidences)
        
        # Calculate balance score (how evenly distributed intents are)
        total_examples = len(examples)
        expected_per_intent = total_examples / len(IntentType)
        balance_score = 1.0 - (max(intent_counts.values()) - min(intent_counts.values())) / total_examples
        
        report = {
            "valid": len(insufficient_intents) == 0 and len(duplicates) < total_examples * 0.1,
            "total_examples": total_examples,
            "intent_distribution": dict(intent_counts),
            "insufficient_intents": insufficient_intents,
            "duplicate_count": len(duplicates),
            "avg_text_length": round(avg_length, 2),
            "avg_confidence": round(avg_confidence, 3),
            "balance_score": round(balance_score, 3),
            "recommendations": []
        }
        
        # Add recommendations
        if insufficient_intents:
            report["recommendations"].append(f"Add more examples for intents: {insufficient_intents}")
        
        if len(duplicates) > total_examples * 0.05:
            report["recommendations"].append("Remove duplicate examples to improve diversity")
        
        if balance_score < 0.7:
            report["recommendations"].append("Balance intent distribution for better training")
        
        if avg_length < 3:
            report["recommendations"].append("Add more complex examples with longer text")
        
        return report
    
    def create_train_test_split(self, examples: List[TrainingExample], 
                              test_ratio: float = 0.2) -> Tuple[List[TrainingExample], List[TrainingExample]]:
        """Split training data into train and test sets
        
        Args:
            examples: List of training examples
            test_ratio: Ratio of examples to use for testing
            
        Returns:
            Tuple of (train_examples, test_examples)
        """
        if not 0.0 < test_ratio < 1.0:
            raise ValueError("Test ratio must be between 0.0 and 1.0")
        
        # Group examples by intent for stratified split
        intent_groups = defaultdict(list)
        for example in examples:
            intent_groups[example.intent].append(example)
        
        train_examples = []
        test_examples = []
        
        # Split each intent group
        for intent, intent_examples in intent_groups.items():
            random.shuffle(intent_examples)
            
            test_size = max(1, int(len(intent_examples) * test_ratio))
            
            test_examples.extend(intent_examples[:test_size])
            train_examples.extend(intent_examples[test_size:])
        
        # Shuffle final sets
        random.shuffle(train_examples)
        random.shuffle(test_examples)
        
        logger.info(f"Split data: {len(train_examples)} train, {len(test_examples)} test")
        return train_examples, test_examples
    
    def augment_training_data(self, examples: List[TrainingExample], 
                            augmentation_factor: int = 2) -> List[TrainingExample]:
        """Augment existing training data with generated examples
        
        Args:
            examples: Existing training examples
            augmentation_factor: Multiplier for data augmentation
            
        Returns:
            Augmented training examples
        """
        augmented = examples.copy()
        
        # Count existing examples per intent
        intent_counts = Counter(example.intent for example in examples)
        
        # Generate additional examples for each intent
        for intent, count in intent_counts.items():
            additional_needed = count * (augmentation_factor - 1)
            if additional_needed > 0:
                new_examples = self.generator._generate_intent_examples(intent, additional_needed)
                augmented.extend(new_examples)
        
        random.shuffle(augmented)
        logger.info(f"Augmented data from {len(examples)} to {len(augmented)} examples")
        return augmented


def create_training_dataset(output_path: str, num_examples_per_intent: int = 100) -> None:
    """Create a complete training dataset and save to file
    
    Args:
        output_path: Path to save the training dataset
        num_examples_per_intent: Number of examples to generate per intent
    """
    generator = TrainingDataGenerator()
    manager = TrainingDataManager()
    
    # Generate training examples
    examples = generator.generate_training_examples(num_examples_per_intent)
    
    # Validate the data
    validation_report = manager.validate_training_data(examples)
    logger.info(f"Training data validation: {validation_report}")
    
    # Save to file
    manager.save_to_file(examples, output_path)
    
    logger.info(f"Created training dataset with {len(examples)} examples at {output_path}")