#!/usr/bin/env python3
"""
Setup script for Voice Shopping Assistant development environment
"""

import os
import sys
import subprocess
import platform


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(f"  Error: {e.stderr}")
        return False


def main():
    """Main setup function"""
    print("Voice Shopping Assistant - Development Environment Setup")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("✗ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✓ Python {sys.version.split()[0]} detected")
    
    # Check if virtual environment exists
    venv_path = "venv"
    if os.path.exists(venv_path):
        print(f"✓ Virtual environment already exists at {venv_path}")
    else:
        print("Creating virtual environment...")
        if not run_command("python -m venv venv", "Virtual environment creation"):
            sys.exit(1)
    
    # Determine activation command based on platform
    if platform.system() == "Windows":
        activate_cmd = "venv\\Scripts\\activate"
        pip_cmd = "venv\\Scripts\\pip"
        python_cmd = "venv\\Scripts\\python"
    else:
        activate_cmd = "source venv/bin/activate"
        pip_cmd = "venv/bin/pip"
        python_cmd = "venv/bin/python"
    
    print(f"\nTo activate the virtual environment, run:")
    print(f"  {activate_cmd}")
    
    # Install dependencies if requested
    if len(sys.argv) > 1 and sys.argv[1] == "--install":
        print("\nInstalling dependencies...")
        
        # Upgrade pip
        run_command(f"{pip_cmd} install --upgrade pip", "Pip upgrade")
        
        # Install requirements
        if os.path.exists("requirements.txt"):
            run_command(f"{pip_cmd} install -r requirements.txt", "Installing requirements")
        
        # Install package in development mode
        run_command(f"{pip_cmd} install -e .", "Installing package in development mode")
        
        # Install spaCy model
        run_command(f"{python_cmd} -m spacy download en_core_web_sm", "Installing spaCy English model")
        
        print("\n✓ Setup complete!")
        print(f"Don't forget to activate your virtual environment: {activate_cmd}")
    else:
        print(f"\nTo install dependencies, run:")
        print(f"  python setup_env.py --install")
        print(f"\nOr manually after activating the environment:")
        print(f"  {activate_cmd}")
        print(f"  pip install -r requirements.txt")
        print(f"  pip install -e .")
        print(f"  python -m spacy download en_core_web_sm")


if __name__ == "__main__":
    main()