#!/usr/bin/env python3
"""
Start both API servers for the complete Agricultural Platform
"""

import subprocess
import sys
import os
import time
import threading
import socket

def check_port(port):
    """Check if a port is already in use"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def kill_process_on_port(port):
    """Kill process running on specified port (Windows)"""
    try:
        # For Windows
        result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        for line in lines:
            if f':{port}' in line and 'LISTENING' in line:
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    print(f"🔄 Killing process {pid} on port {port}")
                    subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True)
                    time.sleep(2)
                    break
    except Exception as e:
        print(f"⚠️ Could not kill process on port {port}: {e}")

def start_unified_api():
    """Start the unified agricultural API on port 8000"""
    print("🌾 Starting Unified Agricultural API on port 8000...")
    try:
        # Check if port is in use and kill if necessary
        if check_port(8000):
            print("🔄 Port 8000 is busy, attempting to free it...")
            kill_process_on_port(8000)
            time.sleep(3)
        
        subprocess.run([sys.executable, "unified_agricultural_api.py"], check=True)
    except KeyboardInterrupt:
        print("\n🌾 Unified API stopped")
    except Exception as e:
        print(f"🌾 Unified API failed: {e}")

def start_agentweaver_api():
    """Start the AgentWeaver API on port 8001"""
    print("🤖 Starting AgentWeaver API on port 8001...")
    time.sleep(3)  # Give unified API time to start first
    try:
        # Check if port is in use and kill if necessary
        if check_port(8001):
            print("🔄 Port 8001 is busy, attempting to free it...")
            kill_process_on_port(8001)
            time.sleep(3)
            
        subprocess.run([sys.executable, "main.py"], check=True)
    except KeyboardInterrupt:
        print("\n🤖 AgentWeaver API stopped")
    except Exception as e:
        print(f"🤖 AgentWeaver API failed: {e}")

def main():
    """Main startup function for both APIs."""
    print("=" * 70)
    print("🌾🤖 DUAL AGRICULTURAL PLATFORM STARTUP")
    print("=" * 70)
    print()
    print("Starting both API servers:")
    print("🌾 Unified Agricultural API: http://localhost:8000")
    print("   - Marketplace, Farmer Profiles, Business Intelligence")
    print("🤖 AgentWeaver API: http://localhost:8001") 
    print("   - Demo Queries, Satellite Analysis, AI Agents")
    print()
    print("📊 Documentation:")
    print("   - http://localhost:8000/docs")
    print("   - http://localhost:8001/docs")
    print()
    print("Press Ctrl+C to stop both servers")
    print("=" * 70)
    print()
    
    try:
        # Start both APIs in separate threads
        unified_thread = threading.Thread(target=start_unified_api, daemon=True)
        agentweaver_thread = threading.Thread(target=start_agentweaver_api, daemon=True)
        
        unified_thread.start()
        agentweaver_thread.start()
        
        # Keep main thread alive
        while unified_thread.is_alive() or agentweaver_thread.is_alive():
            time.sleep(1)
        
    except KeyboardInterrupt:
        print("\n" + "=" * 70)
        print("🛑 Both servers stopped by user")
        print("=" * 70)
    except Exception as e:
        print(f"\n❌ Error starting servers: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
