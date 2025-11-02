#!/usr/bin/env python3
"""
GitHub Repository Setup Script

This script helps you set up and upload the Voice Shopping Assistant to GitHub.
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description=""):
    """Run a shell command and handle errors"""
    print(f"🔄 {description}")
    print(f"   Running: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(f"   ✅ {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error: {e}")
        if e.stderr:
            print(f"   Error details: {e.stderr.strip()}")
        return False

def check_git_installed():
    """Check if Git is installed"""
    try:
        subprocess.run(["git", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def setup_github_repo():
    """Set up GitHub repository"""
    print("🛒 Voice Shopping Assistant - GitHub Setup")
    print("=" * 60)
    
    # Check if Git is installed
    if not check_git_installed():
        print("❌ Git is not installed or not in PATH")
        print("   Please install Git from: https://git-scm.com/downloads")
        return False
    
    print("✅ Git is installed")
    
    # Check if we're already in a git repository
    if os.path.exists('.git'):
        print("⚠️  Already in a Git repository")
        response = input("   Continue with existing repository? (y/n): ")
        if response.lower() != 'y':
            return False
    else:
        # Initialize Git repository
        if not run_command("git init", "Initializing Git repository"):
            return False
    
    # Add all files to Git
    if not run_command("git add .", "Adding files to Git"):
        return False
    
    # Create initial commit
    commit_message = "Initial commit: Voice Shopping Assistant with GUI and API"
    if not run_command(f'git commit -m "{commit_message}"', "Creating initial commit"):
        print("   Note: If no changes to commit, that's okay!")
    
    # Instructions for GitHub
    print("\n" + "=" * 60)
    print("🎉 Local Git repository is ready!")
    print("\n📋 Next Steps - Create GitHub Repository:")
    print("   1. Go to https://github.com/new")
    print("   2. Repository name: voice-shopping-assistant")
    print("   3. Description: AI-powered voice shopping assistant with GUI")
    print("   4. Make it Public (recommended)")
    print("   5. Don't initialize with README (we already have one)")
    print("   6. Click 'Create repository'")
    
    print("\n🔗 After creating the GitHub repository, run these commands:")
    print("   git branch -M main")
    print("   git remote add origin https://github.com/YOUR_USERNAME/voice-shopping-assistant.git")
    print("   git push -u origin main")
    
    print("\n🚀 Or use the GitHub CLI (if installed):")
    print("   gh repo create voice-shopping-assistant --public --push")
    
    return True

def create_github_actions():
    """Create GitHub Actions workflow"""
    print("\n🔧 Creating GitHub Actions workflow...")
    
    # Create .github/workflows directory
    workflows_dir = Path(".github/workflows")
    workflows_dir.mkdir(parents=True, exist_ok=True)
    
    # Create CI workflow
    workflow_content = """name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10', '3.11']

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        python test_api_basic.py
        python test_end_to_end.py
    
    - name: Test GUI components
      run: |
        python demo_gui.py

  lint:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install linting tools
      run: |
        python -m pip install --upgrade pip
        pip install black flake8 mypy
    
    - name: Run linting
      run: |
        black --check voice_shopping_assistant/
        flake8 voice_shopping_assistant/ --max-line-length=100
"""
    
    workflow_file = workflows_dir / "ci.yml"
    with open(workflow_file, 'w') as f:
        f.write(workflow_content)
    
    print(f"   ✅ Created {workflow_file}")
    
    return True

def main():
    """Main setup function"""
    try:
        # Setup Git repository
        if not setup_github_repo():
            print("❌ GitHub setup failed")
            return False
        
        # Create GitHub Actions
        create_github_actions()
        
        # Final instructions
        print("\n" + "=" * 60)
        print("🎉 GitHub Setup Complete!")
        print("\n📁 Repository Contents:")
        print("   ✅ README.md - Comprehensive project documentation")
        print("   ✅ LICENSE - MIT License")
        print("   ✅ requirements.txt - Python dependencies")
        print("   ✅ gui_requirements.txt - GUI-specific dependencies")
        print("   ✅ .gitignore - Git ignore rules")
        print("   ✅ .github/workflows/ci.yml - CI/CD pipeline")
        
        print("\n🚀 Features Ready for GitHub:")
        print("   🎤 Voice Shopping Assistant with Speech-to-Text")
        print("   🖥️ Modern Streamlit GUI with 6 pages")
        print("   🌐 FastAPI REST API with Swagger docs")
        print("   🧪 Comprehensive testing framework")
        print("   📊 Analytics and insights dashboard")
        print("   🛒 Real-time cart management")
        print("   🔍 Smart product search and filtering")
        
        print("\n📞 Support:")
        print("   📧 Issues: Use GitHub Issues for bug reports")
        print("   💬 Discussions: Use GitHub Discussions for questions")
        print("   📖 Docs: See README.md and individual module docs")
        
        return True
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)