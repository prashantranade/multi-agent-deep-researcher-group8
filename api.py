# api.py
from fastapi import FastAPI, BackgroundTasks, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
import io
import pypdf
import docx
import os
import json

from crews.base_crew import ResearchBrief
from crews.router import get_crew
from source_engine.discovery import discover_sources
from source_engine.confidence_scorer import score_sources

app = FastAPI(title="Deep Researcher API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

TASKS_FILE = "tasks_db.json"

def load_tasks() -> Dict[str, Any]:
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading tasks: {e}")
            return {}
    return {}

def save_tasks(tasks_dict: Dict[str, Any]):
    try:
        with open(TASKS_FILE, "w", encoding="utf-8") as f:
            json.dump(tasks_dict, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving tasks: {e}")

# Load persisted tasks on startup
tasks: Dict[str, Dict[str, Any]] = load_tasks()

class DiscoverRequest(BaseModel):
    topic: str

class StartRequest(BaseModel):
    topic: str
    persona: str
    audience: str
    tone: str
    depth: str
    selected_sources: List[Dict[str, Any]]
    selected_artifacts: List[str]
    context_text: Optional[str] = None

@app.post("/api/sources/discover")
def api_discover_sources(payload: DiscoverRequest):
    raw = discover_sources(payload.topic)
    scored = score_sources(raw)
    return scored

def run_crew_task(task_id: str, brief: ResearchBrief):
    try:
        crew = get_crew(brief.persona)
        output = crew.run(brief)
        tasks[task_id] = {
            "status": "complete",
            "artifacts": output.artifacts,
            "notes": getattr(output, "notes", []),
            "error": None
        }
        save_tasks(tasks)
    except Exception as e:
        tasks[task_id] = {
            "status": "failed",
            "artifacts": [],
            "notes": [],
            "error": str(e)
        }
        save_tasks(tasks)

@app.post("/api/research/start")
def api_start_research(payload: StartRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    brief = ResearchBrief(
        topic=payload.topic,
        persona=payload.persona,
        audience=payload.audience,
        tone=payload.tone,
        depth=payload.depth,
        context_text=payload.context_text,
        selected_sources=payload.selected_sources,
        selected_artifacts=payload.selected_artifacts
    )
    
    tasks[task_id] = {
        "status": "running",
        "artifacts": [],
        "notes": [],
        "error": None
    }
    save_tasks(tasks)
    
    background_tasks.add_task(run_crew_task, task_id, brief)
    return {"task_id": task_id, "status": "running"}

@app.get("/api/research/status/{task_id}")
def api_get_status(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return {
        "task_id": task_id,
        "status": tasks[task_id]["status"],
        "notes": tasks[task_id]["notes"],
        "error": tasks[task_id]["error"]
    }

@app.get("/api/research/results/{task_id}")
def api_get_results(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    task = tasks[task_id]
    if task["status"] != "complete":
        raise HTTPException(status_code=400, detail="Task is not complete yet")
    return {
        "task_id": task_id,
        "artifacts": task["artifacts"]
    }

@app.post("/api/context/upload")
async def api_upload_context(file: UploadFile = File(...)):
    filename = file.filename or ""
    content = await file.read()
    text = ""
    
    try:
        if filename.endswith(".pdf"):
            reader = pypdf.PdfReader(io.BytesIO(content))
            pages_text = []
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    pages_text.append(t)
            text = "\n".join(pages_text)
        elif filename.endswith(".docx"):
            doc = docx.Document(io.BytesIO(content))
            text = "\n".join([p.text for p in doc.paragraphs])
        else:
            text = content.decode("utf-8", errors="ignore")
            
        return {"text": text, "status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse document: {str(e)}")
