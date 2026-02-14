
import subprocess
import time
import webbrowser
import sys
import os
import socket
from pathlib import Path

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def main():
    # Configuration
    HOST = "127.0.0.1"
    PORT = 8000
    URL = f"http://{HOST}:{PORT}"
    BACKEND_DIR = Path("backend")
    
    print(f"🚀 Starting Excel to Tally AI Agent111111111...")
    
    # Check if backend directory exists
    if not BACKEND_DIR.exists():
        print(f"❌ Error: 'backend' directory not found in {os.getcwd()}")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Start the FastAPI server using uvicorn via subprocess
    # We use sys.executable to ensure we use the same python interpreter (from venv)
    cmd = [sys.executable, "-m", "uvicorn", "main:app", "--host", HOST, "--port", str(PORT)]
    
    try:
        # Start server process
        print("⏳ Starting server...")
        process = subprocess.Popen(
            cmd,
            cwd=BACKEND_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for server to start
        max_retries = 30
        server_started = False
        
        for i in range(max_retries):
            if is_port_in_use(PORT):
                server_started = True
                break
            time.sleep(0.5)
            print(".", end="", flush=True)
            
        print() # Newline
        
        if server_started:
            print(f"✅ Server started at {URL}")
            print("🌐 Opening browser...")
            webbrowser.open(URL)
            
            print("\n⚠️  Keep this window open while using the application.")
            print("❌ Close this window to stop the server.")
            
            # Stream output efficiently
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(output.strip())
        else:
            print("❌ Failed to start server within timeout.")
            # Print any stderr
            _, stderr = process.communicate()
            print(stderr)
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping server...")
        process.terminate()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
    finally:
        if 'process' in locals():
            process.terminate()

if __name__ == "__main__":
    main()
