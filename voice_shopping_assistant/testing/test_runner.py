"""Test runner for end-to-end conversation testing"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from .conversation_simulator import (
    ConversationSimulator, ConversationScenario, ConversationResult,
    create_test_scenarios
)
from .sample_catalog import create_test_cart_manager, create_test_product_search
from ..models.core import IntentType, EntityType, Intent, Entity, NLPResult
from ..interfaces import NLPProcessorInterface, ResponseGeneratorInterface


class MockNLPProcessor(NLPProcessorInterface):
    """Mock NLP processor for testing"""
    
    def __init__(self):
        self.processing_count = 0
    
    def process(self, text: str, context) -> NLPResult:
        """Mock text processing with simple rule-based logic"""
        self.processing_count += 1
        
        # Simple intent classification based on keywords
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['add', 'put', 'include']):
            intent_type = IntentType.ADD
        elif any(word in text_lower for word in ['remove', 'delete', 'take out']):
            intent_type = IntentType.REMOVE
        elif any(word in text_lower for word in ['search', 'find', 'look for', 'show']):
            intent_type = IntentType.SEARCH
        elif any(word in text_lower for word in ['checkout', 'buy', 'purchase']):
            intent_type = IntentType.CHECKOUT
        else:
            intent_type = IntentType.HELP
        
        # Extract simple entities
        entities = []
        
        # Product entities
        products = ['shirt', 'jeans', 'shoes', 'dress', 'pants', 't-shirt']
        for product in products:
            if product in text_lower:
                entities.append(Entity(
                    type=EntityType.PRODUCT,
                    value=product,
                    confidence=0.9,
                    span=(text_lower.find(product), text_lower.find(product) + len(product))
                ))
        
        # Color entities
        colors = ['red', 'blue', 'green', 'white', 'black', 'yellow']
        for color in colors:
            if color in text_lower:
                entities.append(Entity(
                    type=EntityType.COLOR,
                    value=color,
                    confidence=0.8,
                    span=(text_lower.find(color), text_lower.find(color) + len(color))
                ))
        
        # Size entities
        sizes = ['xs', 's', 'm', 'l', 'xl', 'xxl', '28', '30', '32', '34', '36', '38', '6', '7', '8', '9', '10', '11', '12']
        for size in sizes:
            if size in text_lower:
                entities.append(Entity(
                    type=EntityType.SIZE,
                    value=size,
                    confidence=0.8,
                    span=(text_lower.find(size), text_lower.find(size) + len(size))
                ))
        
        # Quantity entities
        quantities = ['one', 'two', 'three', 'four', 'five', '1', '2', '3', '4', '5']
        for qty in quantities:
            if qty in text_lower:
                entities.append(Entity(
                    type=EntityType.QUANTITY,
                    value=qty,
                    confidence=0.9,
                    span=(text_lower.find(qty), text_lower.find(qty) + len(qty))
                ))
        
        # Create intent with entities
        intent = Intent(
            type=intent_type,
            confidence=0.85,
            entities=entities
        )
        
        # Create NLP result
        return NLPResult(
            original_text=text,
            normalized_text=text.lower().strip(),
            intent=intent,
            entities=entities,
            confidence_score=0.85
        )
    
    def resolve_references(self, entities: List[Entity], context) -> List[Entity]:
        """Mock reference resolution - just return entities as-is"""
        return entities
    
    def process_text(self, text: str, session_id: str) -> NLPResult:
        """Convenience method for testing - delegates to process"""
        return self.process(text, None)
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return {
            "total_processed": self.processing_count,
            "processor_type": "mock"
        }


class MockResponseGenerator(ResponseGeneratorInterface):
    """Mock response generator for testing"""
    
    def generate_response(self, intent: Intent, cart_result: Optional, context) -> str:
        """Generate mock responses based on intent"""
        intent_type = intent.type
        
        if intent_type == IntentType.ADD:
            return "I've added the items to your cart."
        elif intent_type == IntentType.REMOVE:
            return "I've removed the items from your cart."
        elif intent_type == IntentType.SEARCH:
            return "Here are the search results."
        elif intent_type == IntentType.CHECKOUT:
            return "Proceeding to checkout."
        else:
            return "How can I help you with your shopping?"
    
    def generate_error_response(self, error_type: str, details: str) -> str:
        """Generate error response"""
        return f"Error ({error_type}): {details}"
    
    def generate_response_from_nlp(self, nlp_result: NLPResult, cart_result, session_id: str) -> str:
        """Convenience method for testing - delegates to generate_response"""
        return self.generate_response(nlp_result.intent, cart_result, None)


class TestReport:
    """Test report generator"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.results: List[ConversationResult] = []
        self.summary_stats: Dict[str, Any] = {}
    
    def add_results(self, results: List[ConversationResult]):
        """Add conversation results to report"""
        self.results.extend(results)
        self._calculate_summary_stats()
    
    def _calculate_summary_stats(self):
        """Calculate overall summary statistics"""
        if not self.results:
            self.summary_stats = {}
            return
        
        total_scenarios = len(self.results)
        successful_scenarios = sum(1 for r in self.results if r.status.value == "completed")
        
        # Aggregate metrics across all scenarios
        all_metrics = [r.calculate_metrics() for r in self.results]
        
        total_commands = sum(m.get("total_commands", 0) for m in all_metrics)
        successful_commands = sum(m.get("successful_commands", 0) for m in all_metrics)
        
        avg_success_rate = sum(m.get("success_rate", 0) for m in all_metrics) / len(all_metrics)
        avg_intent_accuracy = sum(m.get("intent_accuracy", 0) for m in all_metrics) / len(all_metrics)
        avg_processing_time = sum(m.get("avg_processing_time", 0) for m in all_metrics) / len(all_metrics)
        avg_confidence = sum(m.get("avg_nlp_confidence", 0) for m in all_metrics) / len(all_metrics)
        
        total_time = sum(r.total_time for r in self.results)
        
        self.summary_stats = {
            "test_run_time": datetime.now(),
            "total_scenarios": total_scenarios,
            "successful_scenarios": successful_scenarios,
            "failed_scenarios": total_scenarios - successful_scenarios,
            "scenario_success_rate": successful_scenarios / total_scenarios,
            "total_commands": total_commands,
            "successful_commands": successful_commands,
            "command_success_rate": successful_commands / total_commands if total_commands > 0 else 0,
            "avg_success_rate": avg_success_rate,
            "avg_intent_accuracy": avg_intent_accuracy,
            "avg_processing_time": avg_processing_time,
            "avg_nlp_confidence": avg_confidence,
            "total_execution_time": total_time
        }
    
    def generate_report(self, output_file: Optional[str] = None) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        report = {
            "test_summary": self.summary_stats,
            "scenario_results": [r.to_dict() for r in self.results],
            "generated_at": datetime.now().isoformat()
        }
        
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
        
        return report
    
    def print_summary(self):
        """Print test summary to console"""
        if not self.summary_stats:
            print("No test results available")
            return
        
        print("\n" + "=" * 60)
        print("END-TO-END CONVERSATION TEST SUMMARY")
        print("=" * 60)
        
        stats = self.summary_stats
        
        print(f"Test Run Time: {stats['test_run_time']}")
        print(f"Total Execution Time: {stats['total_execution_time']:.2f} seconds")
        print()
        
        print("SCENARIO RESULTS:")
        print(f"  Total Scenarios: {stats['total_scenarios']}")
        print(f"  Successful: {stats['successful_scenarios']}")
        print(f"  Failed: {stats['failed_scenarios']}")
        print(f"  Success Rate: {stats['scenario_success_rate']:.1%}")
        print()
        
        print("COMMAND RESULTS:")
        print(f"  Total Commands: {stats['total_commands']}")
        print(f"  Successful: {stats['successful_commands']}")
        print(f"  Success Rate: {stats['command_success_rate']:.1%}")
        print()
        
        print("PERFORMANCE METRICS:")
        print(f"  Average Intent Accuracy: {stats['avg_intent_accuracy']:.1%}")
        print(f"  Average NLP Confidence: {stats['avg_nlp_confidence']:.1%}")
        print(f"  Average Processing Time: {stats['avg_processing_time']:.3f} seconds")
        print()
        
        # Print individual scenario results
        print("INDIVIDUAL SCENARIO RESULTS:")
        for result in self.results:
            metrics = result.calculate_metrics()
            status_icon = "✓" if result.status.value == "completed" else "✗"
            print(f"  {status_icon} {result.scenario.name}: {metrics['success_rate']:.1%} success rate")
        
        print("=" * 60)


class EndToEndTestRunner:
    """Main test runner for end-to-end conversation testing"""
    
    def __init__(self):
        """Initialize test runner with mock components"""
        # Create test components
        self.product_search = create_test_product_search()
        self.cart_manager = create_test_cart_manager()
        self.nlp_processor = MockNLPProcessor()
        self.response_generator = MockResponseGenerator()
        
        # Create simulator
        self.simulator = ConversationSimulator(
            nlp_processor=self.nlp_processor,
            cart_manager=self.cart_manager,
            response_generator=self.response_generator
        )
        
        # Test report
        self.report = TestReport()
    
    def run_all_tests(self, output_file: Optional[str] = None) -> Dict[str, Any]:
        """Run all predefined test scenarios
        
        Args:
            output_file: Optional file path to save detailed report
            
        Returns:
            Test report dictionary
        """
        print("Starting end-to-end conversation tests...")
        print(f"Product catalog loaded: {len(self.product_search.products)} products")
        
        # Get test scenarios
        scenarios = create_test_scenarios()
        print(f"Running {len(scenarios)} test scenarios...")
        
        # Run scenarios
        results = self.simulator.run_multiple_scenarios(scenarios)
        
        # Add results to report
        self.report.add_results(results)
        
        # Generate and return report
        report = self.report.generate_report(output_file)
        
        return report
    
    def run_custom_scenario(self, scenario: ConversationScenario) -> ConversationResult:
        """Run a single custom scenario
        
        Args:
            scenario: Custom conversation scenario
            
        Returns:
            Conversation result
        """
        result = self.simulator.run_scenario(scenario)
        self.report.add_results([result])
        return result
    
    def print_results(self):
        """Print test results summary"""
        self.report.print_summary()
    
    def get_simulator_stats(self) -> Dict[str, Any]:
        """Get simulator performance statistics"""
        return self.simulator.get_simulation_stats()


def run_end_to_end_tests(output_file: Optional[str] = None) -> bool:
    """Main function to run end-to-end tests
    
    Args:
        output_file: Optional file path to save detailed report
        
    Returns:
        True if tests passed, False otherwise
    """
    runner = EndToEndTestRunner()
    
    try:
        # Run all tests
        report = runner.run_all_tests(output_file)
        
        # Print results
        runner.print_results()
        
        # Determine overall success
        summary = report["test_summary"]
        success_threshold = 0.8  # 80% success rate required
        
        scenario_success = summary["scenario_success_rate"] >= success_threshold
        command_success = summary["command_success_rate"] >= success_threshold
        
        overall_success = scenario_success and command_success
        
        if overall_success:
            print(f"\n🎉 All tests PASSED! (Success rate: {summary['scenario_success_rate']:.1%})")
        else:
            print(f"\n❌ Tests FAILED! (Success rate: {summary['scenario_success_rate']:.1%})")
        
        return overall_success
        
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        return False


if __name__ == "__main__":
    import sys
    
    # Run tests with optional output file
    output_file = sys.argv[1] if len(sys.argv) > 1 else "test_results.json"
    
    success = run_end_to_end_tests(output_file)
    sys.exit(0 if success else 1)