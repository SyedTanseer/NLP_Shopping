#!/usr/bin/env python3
"""
Simple test to create a working microphone button
"""
import streamlit as st

def create_simple_voice_component():
    """Create a simple working voice component"""
    
    voice_html = """
    <div style="margin-bottom: 1rem;">
        <button id="micButton" onclick="toggleMic()" 
                style="background-color: #1f77b4; color: white; border: none; 
                       padding: 0.5rem 1rem; border-radius: 20px; cursor: pointer;">
            🎤 Click to Speak
        </button>
        <div id="status" style="margin-top: 0.5rem; color: #666;">Ready</div>
        <div id="result" style="margin-top: 0.5rem; padding: 0.5rem; 
                               background: #f0f8ff; border-radius: 4px; display: none;">
            <strong>You said:</strong> <span id="transcript"></span>
        </div>
    </div>

    <script>
    let recognition = null;
    let isListening = false;

    // Initialize speech recognition
    if ('webkitSpeechRecognition' in window) {
        recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';
        
        recognition.onstart = function() {
            isListening = true;
            document.getElementById('micButton').textContent = '🔴 Listening...';
            document.getElementById('micButton').style.backgroundColor = '#dc3545';
            document.getElementById('status').textContent = 'Listening... speak now!';
        };
        
        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            document.getElementById('transcript').textContent = transcript;
            document.getElementById('result').style.display = 'block';
            document.getElementById('status').textContent = 'Got it! Transcript: ' + transcript;
        };
        
        recognition.onend = function() {
            isListening = false;
            document.getElementById('micButton').textContent = '🎤 Click to Speak';
            document.getElementById('micButton').style.backgroundColor = '#1f77b4';
        };
        
        recognition.onerror = function(event) {
            document.getElementById('status').textContent = 'Error: ' + event.error;
            isListening = false;
            document.getElementById('micButton').textContent = '🎤 Click to Speak';
            document.getElementById('micButton').style.backgroundColor = '#1f77b4';
        };
    } else {
        document.getElementById('micButton').disabled = true;
        document.getElementById('status').textContent = 'Speech recognition not supported';
    }

    function toggleMic() {
        if (!recognition) return;
        
        if (isListening) {
            recognition.stop();
        } else {
            recognition.start();
        }
    }
    </script>
    """
    
    st.components.v1.html(voice_html, height=200)

def main():
    st.title("🎤 Simple Voice Test")
    st.write("Testing a simple microphone button")
    
    create_simple_voice_component()
    
    st.write("**Instructions:**")
    st.write("1. Click the microphone button")
    st.write("2. Speak when it turns red")
    st.write("3. Your speech should appear below")

if __name__ == "__main__":
    main()