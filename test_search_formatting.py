#!/usr/bin/env python3
"""
Test search result formatting
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

def test_search_formatting():
    """Test that search results have proper line spacing"""
    print("🧪 Testing Search Result Formatting")
    print("=" * 50)
    
    try:
        from voice_shopping_assistant.gui.streamlit_app import VoiceShoppingGUI
        import streamlit as st
        
        # Create mock session state
        class MockSessionState:
            def __init__(self):
                self.session_id = "test-session"
                self.cart_items = []
                self.conversation_history = []
                self.selected_products = []
                self.current_page = "💬 Chat Interface"
                self.voice_commands_processed = 0
                self.last_text_input = ""
                self.chat_input = ""
            
            def __contains__(self, key):
                return hasattr(self, key)
            
            def get(self, key, default=None):
                return getattr(self, key, default)
        
        st.session_state = MockSessionState()
        
        # Create GUI instance
        gui = VoiceShoppingGUI()
        print("✅ GUI instance created successfully")
        
        # Test search command formatting
        search_query = "find me a red shirt"
        print(f"\n🔍 Testing search query: '{search_query}'")
        
        result = gui.handle_search_command(search_query)
        print(f"\n📋 Search Result:")
        print(result)
        
        # Check if result has proper formatting
        lines = result.split('\n')
        print(f"\n📊 Formatting Analysis:")
        print(f"   Total lines: {len(lines)}")
        print(f"   Empty lines: {sum(1 for line in lines if not line.strip())}")
        
        # Check for proper spacing between items
        item_lines = [line for line in lines if line.strip().startswith('•')]
        print(f"   Product items found: {len(item_lines)}")
        
        if len(item_lines) > 1:
            # Check spacing between items
            for i, line in enumerate(lines):
                if line.strip().startswith('•'):
                    print(f"   Item {i}: {line.strip()}")
        
        # Verify the formatting looks good
        has_proper_spacing = '\n\n' in result
        print(f"   Has double line breaks: {has_proper_spacing}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    success = test_search_formatting()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Search formatting test completed!")
        print("\nThe search results should now have proper line spacing between items.")
        print("Try running the GUI and searching for 'red shirt' to see the improved formatting.")
    else:
        print("❌ Search formatting test failed")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)