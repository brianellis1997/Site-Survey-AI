#!/usr/bin/env python3

import subprocess
import sys
import os
from pathlib import Path

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

def setup_environment():
    """Set up the development environment"""
    print("🚀 Setting up Site Survey AI environment")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Create virtual environment if it doesn't exist
    if not Path("survey-env").exists():
        run_command("python3 -m venv survey-env", "Creating virtual environment")
    
    # Determine activation script
    if sys.platform == "win32":
        activate_script = "survey-env\\Scripts\\activate"
        pip_path = "survey-env\\Scripts\\pip"
    else:
        activate_script = "survey-env/bin/activate"
        pip_path = "survey-env/bin/pip"
    
    # Install dependencies
    install_result = run_command(f"{pip_path} install -r requirements.txt", "Installing dependencies")
    
    if install_result is None:
        print("❌ Failed to install dependencies. Try manually:")
        print(f"   source {activate_script}")
        print("   pip install -r requirements.txt")
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
    print(f"1. Activate virtual environment: source {activate_script}")
    print("2. Edit .env file with your configuration")
    print("3. Run the application: python main.py")
    print("4. Test with example: python example_usage.py")
    
    print("\n📚 API Documentation will be available at:")
    print("   http://localhost:8000/docs (Swagger UI)")
    print("   http://localhost:8000/redoc (ReDoc)")

if __name__ == "__main__":
    setup_environment()