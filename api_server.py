#!/usr/bin/env python3
"""
Veritas API Server - FastAPI backend for frontend integration
Connects the HTML frontend to Python workflows.

Run with: python api_server.py
Then open veritas_frontend.html in browser
"""

import asyncio
import json
import sys
import threading  # --- FIX 1: Import the threading module ---
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import (
    FastAPI, File, HTTPException, UploadFile, WebSocket, WebSocketDisconnect
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from workflows.domain_adaptive_workflow import (
    ResearchDomain, create_domain_adaptive_workflow)
from workflows.enhanced_workflow import create_enhanced_workflow
# Import our workflows
from workflows.simple_workflow import WorkflowError, create_simple_workflow


# Data models for API
class ResearchRequest(BaseModel):
    workflow: str  # "simple", "enhanced", "domain"
    goal: str
    data_file_path: Optional[str] = None
    max_revisions: Optional[int] = 2
    quality_threshold: Optional[int] = 7
    domain: Optional[str] = None


class LogMessage(BaseModel):
    type: str  # "log", "progress", "status"
    level: str  # "info", "success", "warning", "error"
    message: str
    timestamp: str
    progress: Optional[int] = None


class ExecutionResult(BaseModel):
    success: bool
    content: Optional[str] = None
    error: Optional[str] = None
    session_dir: Optional[str] = None
    artifacts: List[str] = []
    metrics: Dict[str, Any] = {}


# Initialize FastAPI app
app = FastAPI(title="Veritas Research API", version="3.1.0")

# --- FIX 2: Global variable to hold the main event loop and a startup event to capture it ---
main_event_loop = None


@app.on_event("startup")
async def startup_event():
    """Capture the main event loop when the application starts."""
    global main_event_loop
    main_event_loop = asyncio.get_running_loop()


# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state for managing execution
execution_state = {
    "is_running": False,
    "current_session": None,
    "websocket_connections": [],
}


# WebSocket manager for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        # Make a copy of the list to iterate over, as disconnect can modify it
        connections = self.active_connections[:]
        for connection in connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception:
                # Connection might be dead, remove it
                self.disconnect(connection)


manager = ConnectionManager()

@app.get("/api/status")
async def get_status():
    """Get current execution status."""
    return {
        "is_running": execution_state["is_running"],
        "current_session": execution_state["current_session"],
        "available_workflows": ["simple", "enhanced", "domain"],
    }


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Handle file upload for data analysis."""
    try:
        # Create uploads directory
        uploads_dir = Path("uploads")
        uploads_dir.mkdir(exist_ok=True)

        # Save uploaded file
        file_path = uploads_dir / file.filename
        content = await file.read()

        with open(file_path, "wb") as f:
            f.write(content)

        return {
            "success": True,
            "file_path": str(file_path),
            "filename": file.filename,
            "size": len(content),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")


async def log_to_websocket(level: str, message: str, progress: Optional[int] = None):
    """Send log message to connected WebSocket clients."""
    log_message = {
        "type": "log",
        "level": level,
        "message": message,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "progress": progress,
    }
    await manager.broadcast(log_message)


async def update_progress(percentage: int, message: str = ""):
    """Send progress update to connected WebSocket clients."""
    progress_message = {
        "type": "progress",
        "percentage": percentage,
        "message": message,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
    }
    await manager.broadcast(progress_message)


# ... (other helper functions like detailed_step_log remain the same)

# Console output redirection system
class WebSocketLogHandler:
    """Redirects print statements to WebSocket clients."""

    def __init__(self):
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr

    def write(self, text):
        self.original_stdout.write(text)
        self.original_stdout.flush()
        if text.strip() and manager.active_connections and main_event_loop:
            if threading.current_thread() is not threading.main_thread():
                asyncio.run_coroutine_threadsafe(
                    self._send_to_websocket(text.strip()), main_event_loop
                )
            else:
                asyncio.create_task(self._send_to_websocket(text.strip()))

    def flush(self):
        self.original_stdout.flush()

    async def _send_to_websocket(self, message: str):
        try:
            level = "info"
            if "ERROR" in message.upper() or "❌" in message:
                level = "error"
            elif "WARNING" in message.upper() or "⚠️" in message:
                level = "warning"
            elif "SUCCESS" in message.upper() or "✅" in message or "✓" in message:
                level = "success"
            await log_to_websocket(level, message)
        except Exception:
            pass

websocket_handler = WebSocketLogHandler()

async def enable_console_forwarding():
    try:
        sys.stdout = websocket_handler
        sys.stderr = websocket_handler
        await log_to_websocket("info", "🔗 Console output forwarding enabled")
    except Exception as e:
        await log_to_websocket("warning", f"Console forwarding setup failed: {e}")

async def disable_console_forwarding():
    try:
        sys.stdout = websocket_handler.original_stdout
        sys.stderr = websocket_handler.original_stderr
        await log_to_websocket("info", "🔗 Console output forwarding disabled")
    except Exception:
        pass

async def execute_workflow_with_logging(workflow_func, *args, **kwargs):
    await enable_console_forwarding()
    try:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, workflow_func, *args, **kwargs)
        return result
    finally:
        await disable_console_forwarding()

@app.post("/api/execute", response_model=ExecutionResult)
async def execute_workflow(request: ResearchRequest):
    if execution_state["is_running"]:
        raise HTTPException(
            status_code=409, detail="Another workflow is already running"
        )
    execution_state["is_running"] = True
    session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    execution_state["current_session"] = session_id
    try:
        # ... (rest of the execution logic is the same as before)
        await log_to_websocket("info", f"Starting {request.workflow} workflow...")
        workflow_instance = None
        if request.workflow == "simple":
            workflow_instance = create_simple_workflow()
        elif request.workflow == "enhanced":
            workflow_instance = create_enhanced_workflow()
        elif request.workflow == "domain":
            domain = ResearchDomain(request.domain) if request.domain else None
            workflow_instance = create_domain_adaptive_workflow(domain)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown workflow: {request.workflow}")
        
        document = await execute_workflow_with_logging(
            workflow_instance.run, request.goal, request.data_file_path
        )
        
        content = document.get_content()
        session_dir = None
        artifacts = []
        if hasattr(workflow_instance, "session_dir") and workflow_instance.session_dir.exists():
            session_dir = str(workflow_instance.session_dir)
            artifacts = [f.name for f in workflow_instance.session_dir.glob("*") if f.is_file()]
        elif hasattr(workflow_instance, "domain_dir") and workflow_instance.domain_dir.exists():
            session_dir = str(workflow_instance.domain_dir)
            artifacts = [f.name for f in workflow_instance.domain_dir.glob("*") if f.is_file()]

        metrics = {
            "word_count": len(content.split()),
            "session_id": session_id,
            # ... other metrics
        }

        return ExecutionResult(
            success=True, content=content, session_dir=session_dir, artifacts=artifacts, metrics=metrics
        )
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        await log_to_websocket("error", error_msg)
        traceback.print_exc()
        return ExecutionResult(success=False, error=error_msg)
    finally:
        execution_state["is_running"] = False
        execution_state["current_session"] = None

@app.post("/api/stop")
async def stop_execution():
    # ... (stop logic remains the same)
    return {"success": True}

@app.get("/api/results/{session_id}")
async def get_results(session_id: str):
    # ... (get results logic remains the same)
    pass

@app.get("/api/download/{session_id}/{filename}")
async def download_file(session_id: str, filename: str):
    # ... (download logic remains the same)
    pass

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# --- NEW: Serve the React Frontend ---
class SPAStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        try:
            return await super().get_response(path, scope)
        except HTTPException as ex:
            if ex.status_code == 404:
                return await super().get_response('index.html', scope)
            else:
                raise ex

app.mount("/", SPAStaticFiles(directory="frontend/build", html=True), name="spa")

def main():
    """Run the API server."""
    print("=" * 60)
    print("Veritas API Server - Frontend Integration".center(60))
    print("=" * 60)
    print("\nStarting FastAPI server...")
    print("Frontend available at: http://localhost:8000")
    print("API documentation: http://localhost:8000/docs")
    print("\nMake sure you have set up your API keys in .env file")
    print("Press Ctrl+C to stop the server\n" + "=" * 60)

    try:
        import uvicorn
    except ImportError as e:
        print(f"ERROR: Missing required dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        sys.exit(1)

    if not Path(".env").exists():
        print("WARNING: .env file not found. Please run: python setup_api_keys.py\n")

    uvicorn.run(
        "api_server:app", host="0.0.0.0", port=8000, reload=False, log_level="info"
    )


if __name__ == "__main__":
    main()