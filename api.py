from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncio
from pathlib import Path
import shutil
import json
import sys
import time

# Import from agent.graph
try:
    from agent.graph import agent, PROJECT_ROOT
    print(f"✅ Successfully imported agent from agent.graph")
    print(f"✅ PROJECT_ROOT: {PROJECT_ROOT}")
    print(f"✅ PROJECT_ROOT (absolute): {PROJECT_ROOT.absolute()}")
except ImportError as e:
    print(f"❌ Error importing from agent.graph: {e}")
    print("Make sure agent/graph.py exists and exports 'agent' and 'PROJECT_ROOT'")
    # Fallback
    PROJECT_ROOT = Path(__file__).parent / "generated_project"
    print(f"⚠️  Using fallback PROJECT_ROOT: {PROJECT_ROOT}")

app = FastAPI(title="Coder Buddy API", version="0.1.0")

# Enable CORS - CRITICAL for frontend to work
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerateRequest(BaseModel):
    user_prompt: str

class GenerateResponse(BaseModel):
    files: dict[str, str]
    status: str
    message: str

def read_generated_files():
    """Read all files from PROJECT_ROOT and return as dict"""
    files = {}
    
    print(f"\n🔍 Searching for files in: {PROJECT_ROOT.absolute()}")
    print(f"   Directory exists: {PROJECT_ROOT.exists()}")
    
    if not PROJECT_ROOT.exists():
        print(f"❌ Directory doesn't exist!")
        return files
    
    # List all items in directory
    all_items = list(PROJECT_ROOT.rglob("*"))
    print(f"   Total items found: {len(all_items)}")
    
    file_count = 0
    for file_path in PROJECT_ROOT.rglob("*"):
        if file_path.is_file():
            relative_path = file_path.relative_to(PROJECT_ROOT)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    files[str(relative_path)] = content
                    file_count += 1
                    print(f"   ✅ [{file_count}] {relative_path} ({len(content)} chars)")
            except Exception as e:
                error_msg = f"# Error reading file: {e}"
                files[str(relative_path)] = error_msg
                print(f"   ❌ {relative_path}: {e}")
    
    print(f"\n📊 Total files read: {len(files)}")
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

@app.post("/api/generate")
async def generate_app(request: GenerateRequest):
    """Generate web application from user prompt"""
    try:
        print(f"\n{'='*60}")
        print(f"🚀 NEW GENERATION REQUEST")
        print(f"{'='*60}")
        print(f"📝 Prompt: {request.user_prompt}")
        print(f"📁 Target directory: {PROJECT_ROOT.absolute()}")
        
        # Clean up previous generation
        if PROJECT_ROOT.exists():
            print(f"🗑️  Cleaning up existing directory...")
            shutil.rmtree(PROJECT_ROOT)
        
        PROJECT_ROOT.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created fresh directory: {PROJECT_ROOT}")
        
        # Run the agent
        print(f"\n⏳ Running agent...")
        start_time = time.time()
        
        result = await asyncio.to_thread(
            agent.invoke,
            {"user_prompt": request.user_prompt},
            {"recursion_limit": 100}
        )
        
        elapsed = time.time() - start_time
        print(f"✅ Agent completed in {elapsed:.2f} seconds")
        
        # Wait a moment for file system to sync
        await asyncio.sleep(0.5)
        
        # Read generated files
        print(f"\n{'='*60}")
        print(f"📖 READING GENERATED FILES")
        print(f"{'='*60}")
        
        files = read_generated_files()
        
        print(f"\n{'='*60}")
        print(f"📤 PREPARING RESPONSE")
        print(f"{'='*60}")
        
        if not files:
            print(f"⚠️  WARNING: No files were generated!")
            print(f"   Agent ran but produced no output")
            print(f"   Check agent logs above")
            
            return JSONResponse(
                content={
                    "files": {},
                    "status": "warning",
                    "message": "Agent completed but no files were generated. Check backend logs."
                },
                status_code=200
            )
        
        # Success!
        print(f"✅ Successfully read {len(files)} files")
        print(f"\n📋 Files to send:")
        for filename in files.keys():
            print(f"   - {filename}")
        
        response_data = {
            "files": files,
            "status": "success",
            "message": f"Generated {len(files)} files successfully"
        }
        
        print(f"\n✅ Sending response with {len(files)} files")
        print(f"{'='*60}\n")
        
        return JSONResponse(content=response_data, status_code=200)
    
    except Exception as e:
        print(f"\n{'='*60}")
        print(f"❌ ERROR DURING GENERATION")
        print(f"{'='*60}")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        print(f"{'='*60}\n")
        
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate application: {str(e)}"
        )

@app.delete("/api/clear")
async def clear_generated_files():
    """Clear all generated files"""
    try:
        if PROJECT_ROOT.exists():
            shutil.rmtree(PROJECT_ROOT)
            return {"status": "success", "message": "Cleared generated files"}
        return {"status": "success", "message": "No files to clear"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🚀 Starting Coder Buddy API Server")
    print("="*60)
    print(f"📁 Project root: {PROJECT_ROOT}")
    print(f"📁 Absolute path: {PROJECT_ROOT.absolute()}")
    print(f"🌐 Server: http://localhost:8000")
    print(f"📚 API Docs: http://localhost:8000/docs")
    print(f"🧪 Test endpoint: http://localhost:8000/api/test")
    print("="*60 + "\n")
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )