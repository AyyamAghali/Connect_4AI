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
    # Change to project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    requirements_path = os.path.join(project_root, 'requirements.txt')
    
    # Check if virtual environment exists
    venv_path = os.path.join(project_root, 'venv')
    if os.path.exists(venv_path):
        # Use venv Python
        if os.name == 'nt':  # Windows
            venv_python = os.path.join(venv_path, 'Scripts', 'python.exe')
        else:  # Unix/Mac
            venv_python = os.path.join(venv_path, 'bin', 'python')
        
        if os.path.exists(venv_python):
            try:
                subprocess.check_call([venv_python, "-m", "pip", "install", "-r", requirements_path])
                print("✓ Dependencies installed successfully")
                return True
            except subprocess.CalledProcessError:
                pass
    
    # Try system Python with --user flag
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "-r", requirements_path])
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Error: Failed to install dependencies")
        print(f"   Try running: python -m venv venv")
        print(f"   Then: source venv/bin/activate (or venv\\Scripts\\activate on Windows)")
        print(f"   Then: pip install -r {requirements_path}")
        return False

def main():
    """Main function to start the server"""
    # Change to project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    os.chdir(project_root)
    
    print("=" * 50)
    print("  Connect 4 AI Game - Starting Server")
    print("=" * 50)
    print()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check for virtual environment
    venv_path = os.path.join(project_root, 'venv')
    if os.path.exists(venv_path):
        print("✓ Virtual environment found")
        # Try to use venv Python
        if os.name == 'nt':  # Windows
            venv_python = os.path.join(venv_path, 'Scripts', 'python.exe')
        else:  # Unix/Mac
            venv_python = os.path.join(venv_path, 'bin', 'python')
        
        if os.path.exists(venv_python):
            print("✓ Using virtual environment Python")
            # Update sys.executable to use venv Python
            sys.executable = venv_python
    
    # Check and install dependencies if needed
    if not check_dependencies():
        print("⚠ Dependencies not found. Installing...")
        if not install_dependencies():
            print()
            print("Please run the setup script first:")
            print("  bash setup_env.sh")
            print("  or")
            print("  python -m venv venv")
            print("  source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
            print("  pip install -r requirements.txt")
            sys.exit(1)
    
    print()
    print("Starting Flask server...")
    print("Server will be available at: http://localhost:5001")
    print("Open http://localhost:5001 in your browser to play!")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    print()
    
    # Import and run the Flask app
    try:
        sys.path.insert(0, project_root)
        from app import app
        app.run(debug=True, port=5001, host='127.0.0.1')
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
