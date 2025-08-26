#!/usr/bin/env python3
"""
Simple development server for AgentWeaver frontend demo
"""
import json
import asyncio
from pathlib import Path
import webbrowser
import time

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import HTMLResponse, FileResponse
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
except ImportError:
    print("FastAPI not installed. Installing now...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "fastapi", "uvicorn"])
    from fastapi import FastAPI, HTTPException
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import HTMLResponse, FileResponse
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn

app = FastAPI(title="AgentWeaver Demo Server")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock agent data
mock_agents = [
    {
        "id": "router",
        "name": "Router Agent",
        "type": "router",
        "status": "idle",
        "progress": 0,
        "capabilities": ["Query Classification", "Intent Detection", "Agent Routing"],
        "metrics": {"tasksCompleted": 156, "avgResponseTime": 1.2, "successRate": 98.5}
    },
    {
        "id": "crop",
        "name": "Crop Selection Agent", 
        "type": "crop",
        "status": "idle",
        "progress": 0,
        "capabilities": ["Crop Recommendation", "Yield Prediction", "Soil Analysis"],
        "metrics": {"tasksCompleted": 89, "avgResponseTime": 3.4, "successRate": 94.2}
    }
]

@app.get("/")
async def read_root():
    return {"message": "AgentWeaver Demo Server Running", "agents": len(mock_agents)}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "agents": len(mock_agents)}

@app.get("/agents")
async def get_agents():
    return {"agents": mock_agents}

@app.post("/query")
async def process_query(query: dict):
    return {
        "status": "received",
        "query": query.get("text", ""),
        "workflow_id": f"wf-{int(time.time())}"
    }

if __name__ == "__main__":
    print("🚀 Starting AgentWeaver Demo Server...")
    print("📊 Backend API will be available at: http://localhost:8000")
    print("🎨 Frontend should be started separately with: npm run dev")
    print("📖 Open http://localhost:8000/docs for API documentation")
    
    # Open browser to API docs
    import threading
    def open_browser():
        time.sleep(2)
        webbrowser.open("http://localhost:8000/docs")
    
    threading.Thread(target=open_browser).start()
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
