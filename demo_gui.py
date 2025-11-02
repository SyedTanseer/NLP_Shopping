#!/usr/bin/env python3
"""
Demo script for Voice Shopping Assistant GUI

This script demonstrates the GUI functionality and can be used
to test the interface components programmatically.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from voice_shopping_assistant.gui import VoiceShoppingGUI
    from voice_shopping_assistant.testing import (
        get_sample_products, get_catalog_statistics,
        EndToEndTestRunner, ScenarioBuilder
    )
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please ensure all dependencies are installed")
    sys.exit(1)


def demo_catalog_features():
    """Demonstrate catalog features"""
    print("🛍️ Product Catalog Demo")
    print("=" * 40)
    
    # Get catalog statistics
    stats = get_catalog_statistics()
    print(f"Total Products: {stats['total_products']}")
    print(f"Categories: {list(stats['categories'].keys())}")
    print(f"Price Range: ${stats['price_range'][0]:.2f} - ${stats['price_range'][1]:.2f}")
    print(f"In Stock: {stats['in_stock_count']}")
    print(f"Out of Stock: {stats['out_of_stock_count']}")
    print()
    
    # Show sample products
    products = get_sample_products()[:5]  # First 5 products
    print("Sample Products:")
    for product in products:
        print(f"- {product.name} ({product.brand}) - ${product.price:.2f}")
        print(f"  Categories: {product.category}")
        print(f"  Colors: {', '.join(product.available_colors[:3])}...")
        print(f"  Stock: {'✅' if product.in_stock else '❌'}")
        print()


def demo_testing_features():
    """Demonstrate testing features"""
    print("🧪 Testing Framework Demo")
    print("=" * 40)
    
    try:
        # Create test runner
        runner = EndToEndTestRunner()
        
        # Run a single scenario
        print("Running basic shopping scenario...")
        scenario = ScenarioBuilder.create_basic_shopping_scenario()
        result = runner.run_custom_scenario(scenario)
        
        # Display results
        metrics = result.calculate_metrics()
        print(f"✅ Scenario Status: {result.status.value}")
        print(f"📊 Success Rate: {metrics['success_rate']:.1%}")
        print(f"🎯 Intent Accuracy: {metrics['intent_accuracy']:.1%}")
        print(f"⏱️ Avg Processing Time: {metrics['avg_processing_time']:.3f}s")
        print(f"💬 Total Commands: {metrics['total_commands']}")
        print()
        
        # Show command details
        print("Command Results:")
        for i, cmd_result in enumerate(result.command_results):
            status = "✅" if cmd_result.success else "❌"
            print(f"{i+1}. {status} {cmd_result.command.text}")
            print(f"   Response: {cmd_result.response_text}")
        
    except Exception as e:
        print(f"❌ Testing demo failed: {e}")


def demo_gui_components():
    """Demonstrate GUI components"""
    print("🖥️ GUI Components Demo")
    print("=" * 40)
    
    try:
        # Create GUI instance
        gui = VoiceShoppingGUI()
        
        print("✅ GUI instance created successfully")
        print(f"📱 Session ID: {gui.session_id if hasattr(gui, 'session_id') else 'Not set'}")
        print("🔧 Available components:")
        print("   - Product browsing and search")
        print("   - Shopping cart management")
        print("   - Chat interface for voice commands")
        print("   - End-to-end testing tools")
        print("   - Analytics and insights dashboard")
        print()
        
        # Test product filtering
        print("Testing product filtering...")
        products = gui.filter_products(
            query="shirt",
            category="clothing", 
            price_range=(0, 100),
            brand="All",
            material="All",
            stock_filter="In Stock"
        )
        print(f"Found {len(products)} shirts under $100")
        
        # Test mock response generation
        print("\nTesting chat responses...")
        test_messages = [
            "add two red shirts to my cart",
            "show me my cart",
            "search for blue jeans",
            "help me with shopping"
        ]
        
        for msg in test_messages:
            response = gui.process_shopping_command(msg)
            print(f"User: {msg}")
            print(f"Assistant: {response}")
            print()
        
    except Exception as e:
        print(f"❌ GUI demo failed: {e}")


def main():
    """Main demo function"""
    print("🛒 Voice Shopping Assistant GUI Demo")
    print("=" * 50)
    print()
    
    # Run demos
    demo_catalog_features()
    demo_testing_features()
    demo_gui_components()
    
    print("🎉 Demo completed successfully!")
    print()
    print("To start the GUI web interface, run:")
    print("  python run_gui.py")
    print()
    print("Or use Streamlit directly:")
    print("  streamlit run voice_shopping_assistant/gui/streamlit_app.py")


if __name__ == "__main__":
    main()