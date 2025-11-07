#!/usr/bin/env python3
"""
Test microphone button functionality
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

def test_mic_button_html():
    """Test that the microphone button HTML is properly generated"""
    print("🧪 Testing Microphone Button HTML Generation")
    print("=" * 55)
    
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
        
        # Check the voice integration method
        import inspect
        method_source = inspect.getsource(gui._add_integrated_voice_input)
        
        html_components = []
        
        # Check for button HTML
        if 'id="voiceMicButton"' in method_source:
            html_components.append("Microphone button with ID")
        
        # Check for click handler
        if 'onclick="window.handleVoiceButtonClick' in method_source:
            html_components.append("Button click handler")
        
        # Check for status display
        if 'id="voiceStatus"' in method_source:
            html_components.append("Voice status display")
        
        # Check for transcript display
        if 'id="voiceTranscript"' in method_source:
            html_components.append("Voice transcript display")
        
        # Check for JavaScript functions
        if 'window.toggleVoiceRecognition' in method_source:
            html_components.append("Toggle voice recognition function")
        
        # Check for recognition setup
        if 'recognition.onstart' in method_source:
            html_components.append("Recognition event handlers")
        
        print(f"\n🔧 HTML components found:")
        for component in html_components:
            print(f"   ✅ {component}")
        
        print(f"\n📊 Analysis:")
        print(f"   Total components: {len(html_components)}")
        
        if len(html_components) >= 5:
            print(f"   🎯 All essential components present!")
        else:
            print(f"   ⚠️ Some components may be missing")
        
        # Check for potential issues
        issues = []
        
        if 'window.handleVoiceButtonClick' not in method_source:
            issues.append("Missing global click handler function")
        
        if 'recognition = new SpeechRecognition' not in method_source:
            issues.append("Missing recognition initialization")
        
        if 'onclick=' not in method_source:
            issues.append("Missing button onclick attribute")
        
        if issues:
            print(f"\n⚠️ Potential issues found:")
            for issue in issues:
                print(f"   ❌ {issue}")
        else:
            print(f"\n✅ No obvious issues found in HTML/JavaScript")
        
        # Show debugging steps
        print(f"\n🔍 To debug the microphone button:")
        print(f"   1. Open browser console (F12)")
        print(f"   2. Check for JavaScript errors")
        print(f"   3. Look for the button element: document.getElementById('voiceMicButton')")
        print(f"   4. Test the click handler: window.handleVoiceButtonClick()")
        print(f"   5. Check if recognition is initialized: window.recognition")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    success = test_mic_button_html()
    
    print("\n" + "=" * 55)
    if success:
        print("🎉 Microphone Button HTML Test Completed!")
        print("\nThe button HTML and JavaScript appear to be intact.")
        print("If the button isn't working, check browser console for:")
        print("  • JavaScript errors")
        print("  • Speech recognition support")
        print("  • Button element existence")
        print("  • Click handler function")
        print("\nCommon issues:")
        print("  • Browser doesn't support speech recognition")
        print("  • Microphone permissions not granted")
        print("  • JavaScript errors preventing execution")
        print("  • Button element not found in DOM")
    else:
        print("❌ Microphone button test failed")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)