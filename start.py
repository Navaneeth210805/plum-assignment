#!/usr/bin/env python3
"""
Startup script for Railway deployment
Handles port configuration and starts the application
"""
import os
import sys
import subprocess

def main():
    print("🚀 Starting Medical Report Simplifier...")
    
    # Get port from environment, default to 8000
    port = os.getenv("PORT", "8000")
    print(f"📡 Using port: {port}")
    
    # Validate port is numeric
    try:
        port_int = int(port)
        if port_int < 1 or port_int > 65535:
            raise ValueError("Port out of range")
    except ValueError as e:
        print(f"❌ Invalid port '{port}': {e}")
        print("🔧 Falling back to port 8000")
        port = "8000"
    
    print("🧪 Running startup validation...")
    try:
        result = subprocess.run([sys.executable, "startup_test.py"], check=True)
        print("✅ Startup validation passed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Startup validation failed: {e}")
        sys.exit(1)
    
    print("🎯 Starting uvicorn server...")
    
    # Start uvicorn
    cmd = [
        "uvicorn", 
        "app.main:app", 
        "--host", "0.0.0.0", 
        "--port", port,
        "--log-level", "info",
        "--access-log"
    ]
    
    print(f"🔧 Command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Server failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
