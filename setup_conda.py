#!/usr/bin/env python3

import subprocess
import sys
import os
from pathlib import Path
import shutil

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return None

def check_conda():
    """Check if conda is available"""
    return shutil.which('conda') is not None

def setup_conda_environment():
    """Set up the development environment using conda"""
    print("🚀 Setting up Site Survey AI environment with Conda")
    print("=" * 55)
    
    # Check if conda is available
    if not check_conda():
        print("❌ Conda not found. Please install Miniconda or Anaconda first.")
        sys.exit(1)
    
    print("✅ Conda detected")
    
    # Check if environment already exists
    env_check = run_command("conda env list | grep survey-ai", "Checking for existing environment")
    
    if not env_check:
        # Create conda environment
        create_result = run_command(
            "conda create -n survey-ai python=3.11 -y", 
            "Creating conda environment 'survey-ai'"
        )
        
        if create_result is None:
            print("❌ Failed to create conda environment")
            sys.exit(1)
    else:
        print("✅ Conda environment 'survey-ai' already exists")
    
    # Install dependencies
    print("📦 Installing dependencies...")
    install_commands = [
        "conda run -n survey-ai pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu",
        "conda run -n survey-ai pip install -r requirements.txt"
    ]
    
    for cmd in install_commands:
        result = run_command(cmd, f"Running: {cmd.split()[-1]}")
        if result is None:
            print(f"❌ Failed to install dependencies")
            print("Try manually:")
            print("  conda activate survey-ai")
            print("  pip install -r requirements.txt")
            sys.exit(1)
    
    # Create .env file from example if it doesn't exist
    if not Path(".env").exists():
        if Path(".env.example").exists():
            run_command("cp .env.example .env", "Creating .env file")
            print("📝 Edit .env file to configure your settings")
    
    # Create necessary directories
    Path("models").mkdir(exist_ok=True)
    Path("chroma_db").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    
    print("\n🎉 Setup completed!")
    print("\nNext steps:")
    print("1. Activate environment: conda activate survey-ai")
    print("2. Edit .env file with your configuration")  
    print("3. Run the application: python main.py")
    print("4. Test with example: python example_usage.py")
    
    print("\n📚 API Documentation will be available at:")
    print("   http://localhost:8000/docs (Swagger UI)")
    print("   http://localhost:8000/redoc (ReDoc)")

if __name__ == "__main__":
    setup_conda_environment()