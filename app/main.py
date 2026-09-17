import os
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.config import settings
from app.graph import app_graph
from app.memory import load_session_state, save_session_turn, get_or_create_session_id

app = FastAPI(
    title="Darukaa.Earth Biodiversity Intelligence AI",
    description="RAG-based AI Environmental Scientist for biodiversity and ecological recommendations.",
    version="1.0.0"
)

# Configure CORS Middleware
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "*")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    session_id: Optional[str] = Field(default=None, description="UUID session ID or null for new session")
    message: str = Field(description="User free-form natural language query")

class JsonChatRequest(BaseModel):
    session_id: Optional[str] = Field(default=None, description="UUID session ID or null for new session")
    metrics: Dict[str, Any] = Field(description="Map of structured environmental metrics (e.g., soil_organic_carbon, rainfall, land_use)")

class ChatResponse(BaseModel):
    session_id: str
    reply_type: str = Field(description="'clarifying_question' or 'recommendation'")
    message: Optional[str] = Field(default=None, description="Clarifying question or response message")
    reasoning_summary: Optional[str] = Field(default=None, description="Multi-metric ecological reasoning summary")
    recommendations: Optional[list] = Field(default=None, description="List of evidence-backed recommendations")
    extracted_metrics: Optional[dict] = Field(default=None, description="Accumulated environmental metrics")
    retrieval_trace: Optional[list] = Field(default=None, description="Retrieved vector chunks metadata trace")

@app.get("/health")
def health_check():
    """Simple 200 OK healthcheck route for cloud hosting platforms."""
    return {
        "status": "healthy",
        "groq_model": settings.GROQ_MODEL_NAME,
        "embedding_model": settings.EMBEDDING_MODEL_NAME
    }

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    """Multi-turn text conversation endpoint with session memory and metric accumulation."""
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
        
    session_id = get_or_create_session_id(request.session_id)
    session_state = load_session_state(session_id)
    
    graph_input = {
        "session_id": session_id,
        "user_input": request.message,
        "extracted_metrics": session_state.get("extracted_metrics", {}),
        "is_complete": False,
        "clarifying_question": None,
        "retrieved_chunks": [],
        "reasoning_summary": "",
        "recommendations": [],
        "final_output": {}
    }
    
    graph_output = app_graph.invoke(graph_input)
    final_payload = graph_output.get("final_output", {})
    accumulated_metrics = final_payload.get("extracted_metrics", {})
    
    save_session_turn(
        session_id=session_id,
        user_message=request.message,
        assistant_response=final_payload,
        accumulated_metrics=accumulated_metrics
    )
    
    return ChatResponse(
        session_id=session_id,
        reply_type=final_payload.get("reply_type", "clarifying_question"),
        message=final_payload.get("message"),
        reasoning_summary=final_payload.get("reasoning_summary"),
        recommendations=final_payload.get("recommendations"),
        extracted_metrics=accumulated_metrics,
        retrieval_trace=final_payload.get("retrieval_trace")
    )

@app.post("/chat/json", response_model=ChatResponse)
def chat_json_endpoint(request: JsonChatRequest):
    """Structured JSON metrics input endpoint bypassing text extraction."""
    if not request.metrics or not isinstance(request.metrics, dict):
        raise HTTPException(status_code=400, detail="Metrics must be a non-empty JSON object.")
        
    session_id = get_or_create_session_id(request.session_id)
    session_state = load_session_state(session_id)
    
    merged_metrics = dict(session_state.get("extracted_metrics", {}))
    for k, v in request.metrics.items():
        if v is not None and v != "":
            merged_metrics[str(k)] = str(v)
            
    metrics_str = ", ".join([f"{k}: {v}" for k, v in merged_metrics.items()])
    user_input_summary = f"Structured environmental metrics provided: {metrics_str}"
    
    graph_input = {
        "session_id": session_id,
        "user_input": user_input_summary,
        "extracted_metrics": merged_metrics,
        "is_complete": False,
        "clarifying_question": None,
        "retrieved_chunks": [],
        "reasoning_summary": "",
        "recommendations": [],
        "final_output": {}
    }
    
    graph_output = app_graph.invoke(graph_input)
    final_payload = graph_output.get("final_output", {})
    accumulated_metrics = final_payload.get("extracted_metrics", {})
    
    save_session_turn(
        session_id=session_id,
        user_message=f"JSON Input Payload: {request.metrics}",
        assistant_response=final_payload,
        accumulated_metrics=accumulated_metrics
    )
    
    return ChatResponse(
        session_id=session_id,
        reply_type=final_payload.get("reply_type", "clarifying_question"),
        message=final_payload.get("message"),
        reasoning_summary=final_payload.get("reasoning_summary"),
        recommendations=final_payload.get("recommendations"),
        extracted_metrics=accumulated_metrics,
        retrieval_trace=final_payload.get("retrieval_trace")
    )

# Mount static frontend directory to serve on /static and root /
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static_assets")
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static_root")

