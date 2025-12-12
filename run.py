#!/usr/bin/env python3
"""
Cross-platform startup script for Connect 4 AI Game
Works on Windows, macOS, and Linux
"""

import sys
import subprocess
import os
import platform

def check_python_version():
    """Check if Python version is 3.7 or higher"""
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✓ Python {sys.version.split()[0]} detected")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import flask
        import flask_cors
        print("✓ Dependencies are installed")
        return True
    except ImportError:
        print("⚠ Dependencies not found. Installing...")
        return False

def install_dependencies():
    """Install dependencies from requirements.txt"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Error: Failed to install dependencies")
        print("   Try running: pip install -r requirements.txt")
        return False

def main():
    """Main function to start the server"""
    print("=" * 50)
    print("  Connect 4 AI Game - Starting Server")
    print("=" * 50)
    print()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check and install dependencies if needed
    if not check_dependencies():
        if not install_dependencies():
            sys.exit(1)
    
    print()
    print("Starting Flask server...")
    print("Server will be available at: http://localhost:50000")
    print("Open index.html in your browser to play!")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    print()
    
    # Import and run the Flask app
    try:
        from app import app
        app.run(debug=True, port=5001, host='127.0.0.1')
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
