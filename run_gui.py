#!/usr/bin/env python3
"""
Launch script for Voice Shopping Assistant GUI

This script starts the Streamlit web interface for the voice shopping assistant.
"""

import sys
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def check_streamlit():
    """Check if Streamlit is installed"""
    try:
        import streamlit
        return True
    except ImportError:
        return False


def install_streamlit():
    """Install Streamlit if not available"""
    print("Streamlit not found. Installing...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit", "plotly", "pandas"])
        print("✓ Streamlit installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to install Streamlit")
        return False


def main():
    """Main launcher function"""
    print("🛒 Voice Shopping Assistant GUI Launcher")
    print("=" * 50)
    
    # Check if Streamlit is available
    if not check_streamlit():
        if not install_streamlit():
            print("Please install Streamlit manually: pip install streamlit plotly pandas")
            sys.exit(1)
    
    # Path to the Streamlit app
    app_path = project_root / "voice_shopping_assistant" / "gui" / "streamlit_app.py"
    
    if not app_path.exists():
        print(f"✗ GUI app not found at {app_path}")
        sys.exit(1)
    
    print(f"🚀 Starting GUI at {app_path}")
    print("📱 The web interface will open in your browser")
    print("🔗 Default URL: http://localhost:8501")
    print("\nPress Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Launch Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(app_path),
            "--server.address", "localhost",
            "--server.port", "8501",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 GUI server stopped")
    except Exception as e:
        print(f"✗ Error starting GUI: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()