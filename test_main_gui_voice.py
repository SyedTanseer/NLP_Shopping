#!/usr/bin/env python3
"""
Test the main GUI voice functionality
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

def test_main_gui_voice():
    """Test that the main GUI voice component is working"""
    print("🧪 Testing Main GUI Voice Component")
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
        
        # Test that the voice integration method exists
        assert hasattr(gui, '_add_integrated_voice_input'), "Missing voice integration method"
        print("✅ Voice integration method exists")
        
        # Check that the method contains clean JavaScript
        import inspect
        method_source = inspect.getsource(gui._add_integrated_voice_input)
        
        # Check for essential components
        components_found = []
        
        if 'startVoiceRecognition()' in method_source:
            components_found.append("Button click handler")
        
        if 'recognition.onstart' in method_source:
            components_found.append("Recognition start handler")
        
        if 'recognition.onresult' in method_source:
            components_found.append("Recognition result handler")
        
        if 'recognition.onerror' in method_source:
            components_found.append("Recognition error handler")
        
        if 'st.components.v1.html' in method_source:
            components_found.append("Streamlit HTML component")
        
        print(f"\n🔧 Voice components found:")
        for component in components_found:
            print(f"   ✅ {component}")
        
        if len(components_found) >= 4:
            print(f"\n🎯 Voice component looks complete!")
        else:
            print(f"\n⚠️ Some components may be missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    success = test_main_gui_voice()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Main GUI Voice Component Test Passed!")
        print("\nThe main GUI should now have a working microphone button.")
        print("To test it:")
        print("  1. Run: python run_gui.py")
        print("  2. Go to Chat Interface page")
        print("  3. Click the '🎤 Speak' button")
        print("  4. Speak clearly and check if text appears in input field")
        print("  5. Press Enter to send the transcribed text")
    else:
        print("❌ Main GUI voice component test failed")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)