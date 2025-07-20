#!/usr/bin/env python3
"""
Setup script for Text2Story Generator
Helps users configure the application and install dependencies
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_banner():
    """Print application banner"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                    Text2Story Generator                      ║
    ║              Instagram Story Automation Tool                 ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False

def check_ffmpeg():
    """Check if FFmpeg is installed"""
    print("\n🎬 Checking FFmpeg installation...")
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        print("✅ FFmpeg is installed")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ FFmpeg is not installed")
        print("\n📋 To install FFmpeg:")
        print("   macOS: brew install ffmpeg")
        print("   Ubuntu: sudo apt install ffmpeg")
        print("   Windows: Download from https://ffmpeg.org/download.html")
        return False

def create_env_file():
    """Create .env file from template"""
    print("\n🔧 Setting up environment variables...")
    
    if os.path.exists(".env"):
        print("⚠️  .env file already exists")
        overwrite = input("Do you want to overwrite it? (y/N): ").lower()
        if overwrite != 'y':
            print("Skipping .env creation")
            return True
    
    if not os.path.exists("env.example"):
        print("❌ env.example file not found")
        return False
    
    # Copy env.example to .env
    with open("env.example", "r") as f:
        content = f.read()
    
    with open(".env", "w") as f:
        f.write(content)
    
    print("✅ .env file created from template")
    print("📝 Please edit .env file with your API keys")
    return True

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    directories = ["uploads", "outputs", "temp", "static"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created {directory}/ directory")
    
    return True

def get_api_keys():
    """Interactive API key setup"""
    print("\n🔑 API Key Setup")
    print("You can set these up later in the .env file")
    
    keys = {
        "OPENAI_API_KEY": "OpenAI API Key (for theme analysis)",
        "PEXELS_API_KEY": "Pexels API Key (for stock videos)",
        "PIXABAY_API_KEY": "Pixabay API Key (for stock media)",
    }
    
    setup_now = input("Do you want to set up API keys now? (y/N): ").lower()
    if setup_now != 'y':
        return True
    
    env_content = []
    with open(".env", "r") as f:
        env_content = f.readlines()
    
    for i, line in enumerate(env_content):
        for key, description in keys.items():
            if line.startswith(f"{key}="):
                print(f"\n{description}")
                value = input(f"Enter your {key}: ").strip()
                if value:
                    env_content[i] = f"{key}={value}\n"
                break
    
    with open(".env", "w") as f:
        f.writelines(env_content)
    
    print("✅ API keys updated")
    return True

def test_setup():
    """Test the setup"""
    print("\n🧪 Testing setup...")
    
    # Test imports
    try:
        import flask
        import moviepy
        import requests
        print("✅ Python dependencies imported successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Test configuration
    try:
        from config import Config
        print("✅ Configuration loaded successfully")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False
    
    return True

def main():
    """Main setup function"""
    print_banner()
    
    print("🚀 Starting setup process...\n")
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Check FFmpeg
    ffmpeg_ok = check_ffmpeg()
    if not ffmpeg_ok:
        print("⚠️  FFmpeg is required for video processing")
        print("   You can install it later and restart the application")
    
    # Create directories
    if not create_directories():
        sys.exit(1)
    
    # Create .env file
    if not create_env_file():
        sys.exit(1)
    
    # Setup API keys
    get_api_keys()
    
    # Test setup
    if not test_setup():
        print("❌ Setup test failed")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("🎉 Setup completed successfully!")
    print("="*60)
    
    print("\n📋 Next steps:")
    print("1. Edit .env file with your API keys")
    print("2. Install FFmpeg if not already installed")
    print("3. Run: python app.py")
    print("4. Open: http://localhost:5000")
    
    print("\n📚 For more information, see README.md")
    print("🆘 For help, check the documentation or create an issue")

if __name__ == "__main__":
    main() 