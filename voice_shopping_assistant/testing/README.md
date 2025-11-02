# End-to-End Testing Framework

This directory contains the end-to-end testing framework for the Voice Shopping Assistant, including sample product catalogs and conversation simulation tools.

## Components

### Sample Product Catalog (`sample_catalog.py`)

A comprehensive product database with 32+ diverse products covering:

- **Categories**: Clothing, footwear, electronics, furniture, sports, books, beauty, toys, food
- **Price Range**: $12.99 - $1,299.99
- **Attributes**: Various sizes, colors, materials, and brands
- **Stock Status**: Mix of in-stock and out-of-stock items

**Usage:**
```python
from voice_shopping_assistant.testing import get_sample_products, get_catalog_statistics

# Get all products
products = get_sample_products()

# Get catalog statistics
stats = get_catalog_statistics()
print(f"Total products: {stats['total_products']}")
```

### Conversation Simulator (`conversation_simulator.py`)

Framework for simulating complete shopping conversations with:

- **Scenario Building**: Pre-built and custom conversation scenarios
- **Command Simulation**: Realistic voice commands with expected outcomes
- **Performance Metrics**: Success rates, processing times, accuracy measurements
- **Result Analysis**: Detailed reporting and statistics

**Key Classes:**
- `ConversationSimulator`: Main simulation engine
- `ConversationScenario`: Complete conversation workflow
- `SimulatedCommand`: Individual voice commands
- `ScenarioBuilder`: Helper for creating test scenarios

### Test Runner (`test_runner.py`)

Automated test execution with:

- **Mock Components**: Lightweight NLP and response generation for testing
- **Comprehensive Reporting**: JSON reports with detailed metrics
- **Performance Analysis**: Processing time and accuracy measurements
- **Success Rate Calculation**: Configurable success thresholds

## Running Tests

### Quick Test
```bash
python test_end_to_end.py
```

### Programmatic Usage
```python
from voice_shopping_assistant.testing import run_end_to_end_tests

# Run all tests with custom output file
success = run_end_to_end_tests("my_test_results.json")

# Create custom test runner
from voice_shopping_assistant.testing import EndToEndTestRunner

runner = EndToEndTestRunner()
report = runner.run_all_tests()
runner.print_results()
```

### Custom Scenarios
```python
from voice_shopping_assistant.testing import (
    ConversationScenario, SimulatedCommand, CommandType, 
    IntentType, EndToEndTestRunner
)

# Create custom scenario
scenario = ConversationScenario(
    name="Custom Test",
    description="My custom shopping workflow",
    commands=[
        SimulatedCommand(
            command_type=CommandType.ADD_ITEM,
            text="add blue jeans to cart",
            expected_intent=IntentType.ADD,
            expected_entities=[
                {"type": "PRODUCT", "value": "jeans"},
                {"type": "COLOR", "value": "blue"}
            ]
        )
    ]
)

# Run custom scenario
runner = EndToEndTestRunner()
result = runner.run_custom_scenario(scenario)
```

## Test Scenarios

### Built-in Scenarios

1. **Basic Shopping**: Simple add items and checkout workflow
2. **Complex Shopping**: Multi-step workflow with search, add, remove, and checkout
3. **Error Handling**: Tests error conditions and edge cases

### Scenario Metrics

Each scenario tracks:
- **Success Rate**: Percentage of successful commands
- **Intent Accuracy**: Correct intent classification rate
- **Processing Time**: Average command processing time
- **NLP Confidence**: Average confidence scores
- **Cart Goal Achievement**: Whether final cart matches expectations

## Test Reports

Generated JSON reports include:

```json
{
  "test_summary": {
    "total_scenarios": 3,
    "successful_scenarios": 3,
    "scenario_success_rate": 1.0,
    "total_commands": 13,
    "command_success_rate": 0.92,
    "avg_intent_accuracy": 0.94,
    "avg_processing_time": 0.001,
    "total_execution_time": 1.41
  },
  "scenario_results": [
    {
      "scenario_name": "Basic Shopping",
      "status": "completed",
      "metrics": { ... },
      "command_results": [ ... ]
    }
  ]
}
```

## Integration with Real Components

To test with real NLP and cart components instead of mocks:

```python
from voice_shopping_assistant.testing import ConversationSimulator
from voice_shopping_assistant.nlp import NLPProcessor
from voice_shopping_assistant.cart import CartManager
from voice_shopping_assistant.response import ResponseGenerator

# Create simulator with real components
simulator = ConversationSimulator(
    nlp_processor=NLPProcessor(),
    cart_manager=CartManager(product_search),
    response_generator=ResponseGenerator()
)

# Run scenarios
scenarios = create_test_scenarios()
results = simulator.run_multiple_scenarios(scenarios)
```

## Performance Benchmarks

The framework measures:
- **Processing Time**: < 1 second per command (target)
- **Success Rate**: > 80% for scenario completion
- **Intent Accuracy**: > 90% for intent classification
- **NLP Confidence**: > 0.8 average confidence score

## Extending the Framework

### Adding New Products
```python
from voice_shopping_assistant.testing.sample_catalog import SampleProductCatalog
from voice_shopping_assistant.models.core import Product

catalog = SampleProductCatalog()
new_product = Product(
    id="custom-001",
    name="Custom Product",
    category="custom",
    price=99.99,
    available_sizes=["one size"],
    available_colors=["blue"],
    material="custom material",
    brand="CustomBrand",
    in_stock=True
)

catalog._products.append(new_product)
```

### Creating Custom Commands
```python
custom_command = SimulatedCommand(
    command_type=CommandType.ADD_ITEM,
    text="add premium headphones to my cart",
    expected_intent=IntentType.ADD,
    expected_entities=[
        {"type": "PRODUCT", "value": "headphones"},
        {"type": "BRAND", "value": "premium"}
    ],
    timeout_seconds=3.0,
    description="Add premium headphones"
)
```

This framework provides comprehensive testing capabilities for validating the voice shopping assistant's end-to-end functionality, performance, and accuracy.