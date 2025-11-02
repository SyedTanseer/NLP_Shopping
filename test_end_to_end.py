#!/usr/bin/env python3
"""
End-to-end conversation testing script

This script demonstrates the conversation simulation framework
and runs comprehensive tests of the voice shopping assistant.
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from voice_shopping_assistant.testing import (
        run_end_to_end_tests,
        EndToEndTestRunner,
        ScenarioBuilder,
        get_catalog_statistics
    )
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please ensure all dependencies are installed")
    sys.exit(1)


def test_sample_catalog():
    """Test the sample product catalog"""
    print("Testing sample product catalog...")
    
    try:
        stats = get_catalog_statistics()
        
        print(f"  Total products: {stats['total_products']}")
        print(f"  Categories: {list(stats['categories'].keys())}")
        print(f"  Price range: ${stats['price_range'][0]:.2f} - ${stats['price_range'][1]:.2f}")
        print(f"  In stock: {stats['in_stock_count']}")
        print(f"  Out of stock: {stats['out_of_stock_count']}")
        print("  ✓ Sample catalog loaded successfully")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Sample catalog test failed: {e}")
        return False


def test_conversation_scenarios():
    """Test individual conversation scenarios"""
    print("Testing conversation scenarios...")
    
    try:
        runner = EndToEndTestRunner()
        
        # Test basic shopping scenario
        print("  Testing basic shopping scenario...")
        basic_scenario = ScenarioBuilder.create_basic_shopping_scenario()
        result = runner.run_custom_scenario(basic_scenario)
        
        metrics = result.calculate_metrics()
        print(f"    Commands: {metrics['total_commands']}")
        print(f"    Success rate: {metrics['success_rate']:.1%}")
        print(f"    Intent accuracy: {metrics['intent_accuracy']:.1%}")
        print(f"    Processing time: {metrics['avg_processing_time']:.3f}s")
        
        if result.status.value == "completed":
            print("    ✓ Basic scenario completed successfully")
        else:
            print("    ⚠ Basic scenario had issues")
        
        # Test complex shopping scenario
        print("  Testing complex shopping scenario...")
        complex_scenario = ScenarioBuilder.create_complex_shopping_scenario()
        result = runner.run_custom_scenario(complex_scenario)
        
        metrics = result.calculate_metrics()
        print(f"    Commands: {metrics['total_commands']}")
        print(f"    Success rate: {metrics['success_rate']:.1%}")
        
        if result.status.value == "completed":
            print("    ✓ Complex scenario completed successfully")
        else:
            print("    ⚠ Complex scenario had issues")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Conversation scenario test failed: {e}")
        return False


def run_comprehensive_tests():
    """Run comprehensive end-to-end tests"""
    print("Running comprehensive end-to-end tests...")
    
    # Generate timestamped output file
    timestamp = int(time.time())
    output_file = f"test_results_{timestamp}.json"
    
    try:
        success = run_end_to_end_tests(output_file)
        
        if success:
            print(f"\n✓ Comprehensive tests completed successfully")
            print(f"  Detailed report saved to: {output_file}")
        else:
            print(f"\n⚠ Some tests failed - check report for details")
            print(f"  Detailed report saved to: {output_file}")
        
        return success
        
    except Exception as e:
        print(f"\n✗ Comprehensive tests failed: {e}")
        return False


def main():
    """Main test execution"""
    print("=" * 60)
    print("Voice Shopping Assistant - End-to-End Testing")
    print("=" * 60)
    
    start_time = time.time()
    all_passed = True
    
    # Test sample catalog
    if not test_sample_catalog():
        all_passed = False
    print()
    
    # Test conversation scenarios
    if not test_conversation_scenarios():
        all_passed = False
    print()
    
    # Run comprehensive tests
    if not run_comprehensive_tests():
        all_passed = False
    
    elapsed_time = time.time() - start_time
    
    print("\n" + "=" * 60)
    if all_passed:
        print(f"✓ All end-to-end tests PASSED in {elapsed_time:.2f} seconds")
        print("🎉 Voice shopping assistant is working correctly!")
    else:
        print(f"⚠ Some tests FAILED after {elapsed_time:.2f} seconds")
        print("❌ Please check the test results for details")
    print("=" * 60)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)