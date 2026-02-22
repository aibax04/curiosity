from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncio
from pathlib import Path
import shutil
import sys
import time
from typing import List
import traceback

# Import from agent.graph
try:
    from agent.graph import agent, PROJECT_ROOT
    from agent.tools import init_project_root
    print(f"Successfully imported agent from agent.graph")
    print(f"PROJECT_ROOT: {PROJECT_ROOT}")
    print(f"PROJECT_ROOT (absolute): {PROJECT_ROOT.absolute()}")
except ImportError as e:
    print(f"Error importing from agent.graph: {e}")
    print("Make sure agent/graph.py exists and exports 'agent' and 'PROJECT_ROOT'")
    # Fallback
    PROJECT_ROOT = Path(__file__).parent / "generated_project"
    print(f"Using fallback PROJECT_ROOT: {PROJECT_ROOT}")
    
    def init_project_root():
        await asyncio.to_thread(PROJECT_ROOT.mkdir, parents=True, exist_ok=True)
        return str(PROJECT_ROOT)

app = FastAPI(title="Coder Buddy API", version="0.1.0")

# Enable CORS - CRITICAL for frontend to work
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active WebSocket connections
active_connections: List[WebSocket] = []

class GenerateRequest(BaseModel):
    user_prompt: str

class GenerateResponse(BaseModel):
    files: dict[str, str]
    status: str
    message: str

async def broadcast_log(message: str, msg_type: str = "log"):
    """Send log message to all connected WebSockets"""
    disconnected = []
    for connection in active_connections:
        try:
            await connection.send_json({
                "type": msg_type,
                "message": message
            })
        except Exception:
            disconnected.append(connection)
    
    # Remove disconnected connections
    for conn in disconnected:
        try:
            active_connections.remove(conn)
        except ValueError:
            pass

def read_generated_files():
    """Read all files from PROJECT_ROOT and return as dict"""
    files = {}
    
    print(f"\nSearching for files in: {PROJECT_ROOT.absolute()}")
    print(f"Directory exists: {PROJECT_ROOT.exists()}")
    
    if not PROJECT_ROOT.exists():
        print(f"Directory doesn't exist!")
        return files
    
    # List all items in directory
    all_items = list(PROJECT_ROOT.rglob("*"))
    print(f"Total items found: {len(all_items)}")
    
    file_count = 0
    for file_path in PROJECT_ROOT.rglob("*"):
        if file_path.is_file():
            relative_path = file_path.relative_to(PROJECT_ROOT)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    files[str(relative_path)] = content
                    file_count += 1
                    print(f"[{file_count}] {relative_path} ({len(content)} chars)")
            except Exception as e:
                error_msg = f"# Error reading file: {e}"
                files[str(relative_path)] = error_msg
                print(f"Error reading {relative_path}: {e}")
    
    print(f"\nTotal files read: {len(files)}")
    return files

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Coder Buddy API",
        "version": "0.1.0",
        "status": "running",
        "project_root": str(PROJECT_ROOT.absolute()),
        "endpoints": {
            "health": "/health",
            "generate": "/api/generate",
            "test": "/api/test",
            "clear": "/api/clear",
            "ws": "/ws",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    files = read_generated_files()
    return {
        "status": "healthy",
        "project_root": str(PROJECT_ROOT.absolute()),
        "project_root_exists": PROJECT_ROOT.exists(),
        "files_found": len(files),
        "filenames": list(files.keys()) if files else []
    }

@app.get("/api/test")
async def test_read_files():
    """Test endpoint to check if backend can read generated files"""
    files = read_generated_files()
    
    return {
        "project_root": str(PROJECT_ROOT.absolute()),
        "files_found": len(files),
        "files": files,
        "status": "success" if files else "no_files",
        "message": f"Found {len(files)} files" if files else "No files found in generated_project"
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time logs"""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        await websocket.send_json({
            "type": "connection",
            "message": "Connected to backend"
        })
        
        # Keep connection alive
        while True:
            try:
                # Wait for messages or ping to keep alive
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
            except asyncio.TimeoutError:
                # Send ping to keep connection alive
                try:
                    await websocket.send_json({"type": "ping"})
                except:
                    break
            except WebSocketDisconnect:
                break
            
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)
        print("WebSocket disconnected")

@app.post("/api/generate")
async def generate_app(request: GenerateRequest):
    """Generate web application from user prompt"""
    
    try:
        print("\n" + "="*60)
        print("NEW GENERATION REQUEST")
        print("="*60)
        print(f"Prompt: {request.user_prompt}")
        print(f"Target directory: {PROJECT_ROOT.absolute()}")
        
        await broadcast_log("=" * 60, "log")
        await broadcast_log("NEW GENERATION REQUEST", "info")
        await broadcast_log("=" * 60, "log")
        await broadcast_log(f"Prompt: {request.user_prompt}", "info")
        await broadcast_log(f"Target directory: {PROJECT_ROOT.absolute()}", "info")
        
        # Clean up previous generation
        if PROJECT_ROOT.exists():
            print("Cleaning up existing directory...")
            await broadcast_log("Cleaning up existing directory...", "info")
            await asyncio.to_thread(shutil.rmtree, PROJECT_ROOT)
        
        await asyncio.to_thread(PROJECT_ROOT.mkdir, parents=True, exist_ok=True)
        print(f"Created fresh directory: {PROJECT_ROOT}")
        await broadcast_log("Created fresh directory", "success")
        
        # Run the agent
        print("\nRunning agent...")
        await broadcast_log("\nRunning agent...", "info")
        start_time = time.time()
        
        # Run agent in thread to not block
        try:
            result = await asyncio.to_thread(
                agent.invoke,
                {"user_prompt": request.user_prompt},
                {"recursion_limit": 100}
            )
            print(f"Agent result: {result}")
        except Exception as agent_error:
            print(f"Agent execution error: {agent_error}")
            print(traceback.format_exc())
            await broadcast_log(f"Agent error: {str(agent_error)}", "error")
            raise
        
        elapsed = time.time() - start_time
        print(f"Agent completed in {elapsed:.2f} seconds")
        await broadcast_log(f"Agent completed in {elapsed:.2f} seconds", "success")
        
        # Wait a moment for file system to sync
        await asyncio.sleep(1.0)
        
        # Read generated files
        print("\nReading generated files...")
        await broadcast_log("\nReading generated files...", "info")
        
        files = read_generated_files()
        
        if not files:
            print("WARNING: No files were generated!")
            await broadcast_log("WARNING: No files were generated!", "warning")
            
            return JSONResponse(
                content={
                    "files": {},
                    "status": "warning",
                    "message": "Agent completed but no files were generated. Check backend logs."
                },
                status_code=200
            )
        
        # Success!
        print(f"Successfully read {len(files)} files")
        await broadcast_log(f"Successfully read {len(files)} files", "success")
        
        for filename in files.keys():
            print(f"   - {filename}")
            await broadcast_log(f"   - {filename}", "log")
        
        response_data = {
            "files": files,
            "status": "success",
            "message": f"Generated {len(files)} files successfully"
        }
        
        print(f"\nGeneration complete!")
        await broadcast_log("\nGeneration complete!", "success")
        await broadcast_log("=" * 60, "log")
        
        return JSONResponse(content=response_data, status_code=200)
    
    except Exception as e:
        error_msg = f"ERROR: {str(e)}"
        print(f"\n{error_msg}")
        print(traceback.format_exc())
        
        await broadcast_log(error_msg, "error")
        
        # Send traceback line by line
        tb = traceback.format_exc()
        for line in tb.split('\n'):
            if line.strip():
                await broadcast_log(line, "error")
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate application: {str(e)}"
        )

@app.delete("/api/clear")
async def clear_generated_files():
    """Clear all generated files"""
    try:
        if PROJECT_ROOT.exists():
            await asyncio.to_thread(shutil.rmtree, PROJECT_ROOT)
            return {"status": "success", "message": "Cleared generated files"}
        return {"status": "success", "message": "No files to clear"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("Starting Coder Buddy API Server")
    print("="*60)
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Absolute path: {PROJECT_ROOT.absolute()}")
    print(f"Server: http://localhost:8000")
    print(f"API Docs: http://localhost:8000/docs")
    print(f"Test endpoint: http://localhost:8000/api/test")
    print(f"WebSocket: ws://localhost:8000/ws")
    print("="*60 + "\n")
    
    # Initialize project root
    init_project_root()
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )