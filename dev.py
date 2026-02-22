import subprocess
import sys
import webbrowser
import time
from pathlib import Path
import threading
import os

def setup_frontend():
    """Ensure frontend directory and index.html exist"""
    frontend_dir = Path(__file__).parent / "frontend"
    frontend_dir.mkdir(exist_ok=True)
    
    # Check if index.html exists, if not create it
    index_path = frontend_dir / "index.html"
    if not index_path.exists():
        print("⚠️  Frontend index.html not found. Creating from create_frontend.py...")
        try:
            # Run create_frontend.py to generate the HTML
            subprocess.run([sys.executable, "create_frontend.py"], check=True)
            
            # create_frontend.py already writes to frontend/index.html
            if index_path.exists():
                print("✅ Created frontend/index.html")
            else:
                print(f"❌ Expected frontend/index.html not found after running create_frontend.py")
                return False
        except Exception as e:
            print(f"❌ Error creating frontend: {e}")
            print("Please run create_frontend.py manually first")
            return False
    return True

def run_backend():
    """Run FastAPI backend"""
    print("🔧 Starting backend server...")
    subprocess.run([sys.executable, "api.py"])

def run_frontend():
    """Run frontend server"""
    frontend_dir = Path(__file__).parent / "frontend"
    print(f"🎨 Starting frontend server from {frontend_dir}...")
    
    # Use Python's built-in HTTP server
    subprocess.run(
        [sys.executable, "-m", "http.server", "3000", "--bind", "127.0.0.1"],
        cwd=frontend_dir
    )

def open_browser():
    """Open browser after servers start"""
    time.sleep(3)  # Wait for servers to start
    print("🌐 Opening browser...")
    webbrowser.open("http://localhost:3000")

def main():
    # Setup frontend first
    if not setup_frontend():
        sys.exit(1)
    
    print("\n" + "="*60)
    print("🚀 Starting Coder Buddy Application")
    print("="*60)
    print("\n📡 Backend API: http://localhost:8000")
    print("🎨 Frontend UI: http://localhost:3000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("📚 API ReDoc: http://localhost:8000/redoc")
    print("\n⏳ Waiting for servers to start...")
    print("💡 Press Ctrl+C to stop all servers\n")
    print("="*60 + "\n")
    
    # Start backend in thread
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()
    
    # Wait a moment for backend to start
    time.sleep(2)
    
    # Start frontend in thread
    frontend_thread = threading.Thread(target=run_frontend, daemon=True)
    frontend_thread.start()
    
    # Open browser
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down all servers...")
        print("👋 Goodbye!")
        sys.exit(0)

if __name__ == "__main__":
    main()