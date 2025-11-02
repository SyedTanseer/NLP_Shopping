#!/usr/bin/env python3
"""Demo script for intent classification system"""

import sys
sys.path.append('.')

from voice_shopping_assistant.nlp.intent_classifier import create_intent_classifier
from voice_shopping_assistant.nlp.training_data import TrainingDataGenerator, TrainingDataManager

def demo_intent_classification():
    """Demonstrate intent classification functionality"""
    print("=== Voice Shopping Assistant - Intent Classification Demo ===\n")
    
    # Create intent classifier
    print("1. Loading intent classifier...")
    classifier = create_intent_classifier()
    
    # Show model info
    model_info = classifier.get_model_info()
    print(f"   Model loaded: {model_info['model_loaded']}")
    print(f"   Supported intents: {', '.join(model_info['supported_intents'])}")
    print(f"   Confidence threshold: {model_info['confidence_threshold']}")
    print()
    
    # Test sample commands
    test_commands = [
        "add two red shirts to my cart",
        "remove the blue jeans",
        "search for black sneakers",
        "I want to checkout now",
        "help me with shopping",
        "cancel my order"
    ]
    
    print("2. Testing intent classification:")
    for command in test_commands:
        result = classifier.classify(command)
        print(f"   '{command}'")
        print(f"   -> Intent: {result.type.value} (confidence: {result.confidence:.3f})")
        print()
    
    # Demonstrate batch classification
    print("3. Batch classification:")
    batch_results = classifier.batch_classify(test_commands)
    for i, (command, result) in enumerate(zip(test_commands, batch_results)):
        print(f"   {i+1}. {result.type.value} ({result.confidence:.3f})")
    print()

def demo_training_data():
    """Demonstrate training data generation"""
    print("=== Training Data Generation Demo ===\n")
    
    # Create training data generator
    generator = TrainingDataGenerator()
    
    # Generate sample training data
    print("1. Generating training examples...")
    examples = generator.generate_training_examples(num_examples_per_intent=5)
    print(f"   Generated {len(examples)} examples")
    print()
    
    # Show sample examples for each intent
    print("2. Sample training examples:")
    from collections import defaultdict
    examples_by_intent = defaultdict(list)
    for example in examples:
        examples_by_intent[example.intent].append(example)
    
    for intent, intent_examples in examples_by_intent.items():
        print(f"   {intent.value.upper()}:")
        for i, example in enumerate(intent_examples[:3]):  # Show first 3
            print(f"     {i+1}. '{example.text}'")
        print()
    
    # Validate training data
    print("3. Training data validation:")
    manager = TrainingDataManager()
    validation_report = manager.validate_training_data(examples)
    
    print(f"   Valid: {validation_report['valid']}")
    print(f"   Total examples: {validation_report['total_examples']}")
    print(f"   Balance score: {validation_report['balance_score']:.3f}")
    print(f"   Average text length: {validation_report['avg_text_length']} words")
    
    if validation_report['recommendations']:
        print("   Recommendations:")
        for rec in validation_report['recommendations']:
            print(f"     - {rec}")
    print()

def main():
    """Main demo function"""
    try:
        demo_intent_classification()
        demo_training_data()
        
        print("=== Demo completed successfully! ===")
        print("\nNext steps:")
        print("- Fine-tune the DistilBERT model with generated training data")
        print("- Integrate with entity extraction (Task 5)")
        print("- Connect to cart management system (Task 6)")
        
    except Exception as e:
        print(f"Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()