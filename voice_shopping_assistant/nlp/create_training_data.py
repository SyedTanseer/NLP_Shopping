#!/usr/bin/env python3
"""Script to create training data for intent classification"""

import argparse
import logging
from pathlib import Path

from .training_data import create_training_dataset, TrainingDataManager, TrainingDataGenerator


def main():
    """Main function to create training data"""
    parser = argparse.ArgumentParser(description="Create training data for intent classification")
    parser.add_argument("--output", "-o", type=str, default="training_data.json",
                       help="Output file path for training data")
    parser.add_argument("--examples-per-intent", "-n", type=int, default=100,
                       help="Number of examples to generate per intent")
    parser.add_argument("--format", "-f", choices=["json", "csv"], default="json",
                       help="Output format")
    parser.add_argument("--validate", action="store_true",
                       help="Validate generated training data")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Ensure output file has correct extension
    output_path = Path(args.output)
    if output_path.suffix.lower() not in ['.json', '.csv']:
        output_path = output_path.with_suffix(f'.{args.format}')
    
    print(f"Creating training dataset with {args.examples_per_intent} examples per intent...")
    
    # Create training dataset
    create_training_dataset(str(output_path), args.examples_per_intent)
    
    if args.validate:
        print("Validating generated training data...")
        manager = TrainingDataManager()
        examples = manager.load_from_file(str(output_path))
        validation_report = manager.validate_training_data(examples)
        
        print("\nValidation Report:")
        print(f"Valid: {validation_report['valid']}")
        print(f"Total examples: {validation_report['total_examples']}")
        print(f"Intent distribution: {validation_report['intent_distribution']}")
        print(f"Average text length: {validation_report['avg_text_length']} words")
        print(f"Balance score: {validation_report['balance_score']}")
        
        if validation_report['recommendations']:
            print("\nRecommendations:")
            for rec in validation_report['recommendations']:
                print(f"- {rec}")
    
    print(f"\nTraining data created successfully: {output_path}")


if __name__ == "__main__":
    main()