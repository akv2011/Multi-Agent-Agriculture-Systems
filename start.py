#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple startup script for the Unified Agricultural Platform.
This is the ONLY file you need to run to start the complete system.
"""

import subprocess
import sys
import os
import time

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required")
        sys.exit(1)
    print(f"Python {sys.version.split()[0]} detected - OK")

def install_dependencies():
    """Install required dependencies."""
    print("Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        print("Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        sys.exit(1)

def start_api_server():
    """Start the unified API server."""
    print("Starting Unified Agricultural API Server...")
    print("Server will be available at: http://localhost:8000")
    print("API Documentation: http://localhost:8000/docs")
    print("Press Ctrl+C to stop the server")
    print()
    
    try:
        # Start the server
        subprocess.run([sys.executable, "unified_agricultural_api.py"], check=True)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"Server failed to start: {e}")
        sys.exit(1)

def main():
    """Main startup function."""
    print("=" * 60)
    print("UNIFIED AGRICULTURAL PLATFORM STARTUP")
    print("=" * 60)
    print()
    
    # Check system requirements
    check_python_version()
    
    # Install dependencies
    install_dependencies()
    
    # Start the server
    start_api_server()

if __name__ == "__main__":
    main()
