import json
import logging
from typing import TypedDict, List, Dict, Any, Optional
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END

from app.config import settings
from app.prompts import METRICS_EXTRACTION_PROMPT, REASONING_PROMPT, RECOMMENDATION_PROMPT
from app.retrieval import retrieve_relevant_chunks
from app.validator import verify_and_sanitize_recommendations

logger = logging.getLogger(__name__)

class GraphState(TypedDict):
    session_id: str
    user_input: str
    extracted_metrics: Dict[str, Any]
    is_complete: bool
    clarifying_question: Optional[str]
    retrieved_chunks: List[Dict[str, Any]]
    reasoning_summary: str
    recommendations: List[Dict[str, Any]]
    final_output: Dict[str, Any]

def get_llm():
    """Initialize ChatGroq LLM instance."""
    return ChatGroq(
        groq_api_key=settings.GROQ_API_KEY,
        model_name=settings.GROQ_MODEL_NAME,
        temperature=0.1
    )

def infer_geo_climate_context(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Infer climate zone and regional context from optional geo-coordinates."""
    lat = metrics.get("latitude")
    lon = metrics.get("longitude")
    
    if lat is not None:
        try:
            lat_val = float(lat)
            if -23.5 <= lat_val <= 23.5 and "region_type" not in metrics:
                metrics["region_type"] = "tropical"
                metrics["geo_climate_zone"] = "Tropical Intertropical Zone (Lat: " + str(lat_val) + ")"
            elif (23.5 < abs(lat_val) <= 50) and "region_type" not in metrics:
                metrics["region_type"] = "temperate"
                metrics["geo_climate_zone"] = "Mid-Latitude Temperate Zone (Lat: " + str(lat_val) + ")"
        except (ValueError, TypeError):
            pass
    return metrics

def extract_metrics_node(state: GraphState) -> Dict[str, Any]:
    """Extract environmental metrics and geo-coordinates from user input using Groq LLM."""
    logger.info("[LangGraph Node]: Extracting environmental metrics & geo-coordinates...")
    user_input = state.get("user_input", "")
    existing_metrics = state.get("extracted_metrics", {}) or {}
    
    llm = get_llm()
    prompt = METRICS_EXTRACTION_PROMPT + f"\n\"{user_input}\""
    
    try:
        response = llm.invoke(prompt)
        text_resp = response.content.strip()
        
        if "```json" in text_resp:
            text_resp = text_resp.split("```json")[1].split("```")[0].strip()
        elif "```" in text_resp:
            text_resp = text_resp.split("```")[1].split("```")[0].strip()
            
        new_metrics = json.loads(text_resp)
    except Exception as e:
        logger.warning(f"Error parsing metrics JSON ({e}). Utilizing fallback.")
        new_metrics = {}
        
    merged_metrics = dict(existing_metrics)
    for k, v in new_metrics.items():
        if v is not None and v != "":
            merged_metrics[k] = v
            
    merged_metrics = infer_geo_climate_context(merged_metrics)
    return {"extracted_metrics": merged_metrics}

def completeness_check_node(state: GraphState) -> Dict[str, Any]:
    """Check if at least 3 environmental variables (or geo context) are known."""
    logger.info("[LangGraph Node]: Performing completeness check...")
    metrics = state.get("extracted_metrics", {})
    known_metrics = {k: v for k, v in metrics.items() if v is not None and v != ""}
    
    is_complete = len(known_metrics) >= 3
    clarifying_question = None
    
    if not is_complete:
        clarifying_question = (
            f"To provide scientifically-grounded multi-metric recommendations, I need a bit more detail about your land. "
            f"Could you please share your soil organic carbon %, annual rainfall pattern, soil pH, current land use / crop type, or location coordinates?"
        )
        
    return {
        "is_complete": is_complete,
        "clarifying_question": clarifying_question
    }

def retrieve_node(state: GraphState) -> Dict[str, Any]:
    """Retrieve top-k relevant scientific evidence chunks from vector store."""
    logger.info("[LangGraph Node]: Retrieving scientific evidence chunks...")
    metrics = state.get("extracted_metrics", {})
    user_input = state.get("user_input", "")
    
    metrics_str = ", ".join([f"{k}: {v}" for k, v in metrics.items() if v])
    query = f"{user_input}. Extracted metrics: {metrics_str}"
    
    chunks = retrieve_relevant_chunks(query, top_k=4)
    return {"retrieved_chunks": chunks}

def multi_metric_reasoning_node(state: GraphState) -> Dict[str, Any]:
    """Reason across at least 3 environmental variables using scientific evidence."""
    logger.info("[LangGraph Node]: Executing multi-metric scientific reasoning...")
    metrics = state.get("extracted_metrics", {})
    chunks = state.get("retrieved_chunks", [])
    
    chunks_text = "\n\n".join([f"Source: {c['source_title']} (Category: {c['category']})\n{c['content']}" for c in chunks])
    metrics_json = json.dumps(metrics, indent=2)
    
    prompt = REASONING_PROMPT.format(
        retrieved_chunks_text=chunks_text,
        extracted_metrics_json=metrics_json
    )
    
    llm = get_llm()
    response = llm.invoke(prompt)
    reasoning_summary = response.content.strip()
    
    return {"reasoning_summary": reasoning_summary}

def recommendation_generator_node(state: GraphState) -> Dict[str, Any]:
    """Generate structured, cited recommendations matching PRD FR3 schema."""
    logger.info("[LangGraph Node]: Generating evidence-backed recommendations...")
    metrics = state.get("extracted_metrics", {})
    reasoning = state.get("reasoning_summary", "")
    chunks = state.get("retrieved_chunks", [])
    
    chunks_text = "\n\n".join([f"Source: {c['source_title']} (Category: {c['category']})\n{c['content']}" for c in chunks])
    metrics_json = json.dumps(metrics, indent=2)
    
    prompt = RECOMMENDATION_PROMPT.format(
        retrieved_chunks_text=chunks_text,
        extracted_metrics_json=metrics_json,
        reasoning_summary=reasoning
    )
    
    llm = get_llm()
    try:
        response = llm.invoke(prompt)
        text_resp = response.content.strip()
        
        if "```json" in text_resp:
            text_resp = text_resp.split("```json")[1].split("```")[0].strip()
        elif "```" in text_resp:
            text_resp = text_resp.split("```")[1].split("```")[0].strip()
            
        raw_recommendations = json.loads(text_resp)
        if not isinstance(raw_recommendations, list):
            raw_recommendations = [raw_recommendations]
    except Exception as e:
        logger.warning(f"Error parsing recommendation JSON ({e}). Utilizing seed evidence fallbacks.")
        raw_recommendations = [
            {
                "intervention": "Introduce legume-based cover crops",
                "mechanism": "Nitrogen fixation increases soil organic carbon and microbial turnover rate, stabilizing soil structure.",
                "impacted_metrics": ["soil_organic_carbon", "soil_moisture", "species_richness"],
                "expected_improvement": "15-25% increase in SOC over 2-3 years, +15% moisture retention",
                "time_horizon": "medium",
                "citation": "FAO Technical Manual on Soil Organic Carbon Management (2020)",
                "confidence": "high"
            }
        ]
        
    sanitized_recommendations = verify_and_sanitize_recommendations(raw_recommendations, chunks)
    return {"recommendations": sanitized_recommendations}

def format_output_node(state: GraphState) -> Dict[str, Any]:
    """Format final response payload with retrieval tracing for auditability."""
    logger.info("[LangGraph Node]: Formatting final output payload with retrieval trace...")
    session_id = state.get("session_id", "")
    is_complete = state.get("is_complete", False)
    chunks = state.get("retrieved_chunks", [])
    
    # Expose retrieval trace (chunk IDs, source titles, similarity scores)
    retrieval_trace = [
        {
            "id": c.get("id"),
            "source_title": c.get("source_title"),
            "category": c.get("category"),
            "similarity": round(float(c.get("similarity", 0.0)), 4)
        } for c in chunks
    ]
    
    if not is_complete:
        final_output = {
            "session_id": session_id,
            "reply_type": "clarifying_question",
            "message": state.get("clarifying_question", "Could you provide more environmental metrics?"),
            "extracted_metrics": state.get("extracted_metrics", {})
        }
    else:
        final_output = {
            "session_id": session_id,
            "reply_type": "recommendation",
            "reasoning_summary": state.get("reasoning_summary", ""),
            "recommendations": state.get("recommendations", []),
            "extracted_metrics": state.get("extracted_metrics", {}),
            "retrieval_trace": retrieval_trace
        }
        
    return {"final_output": final_output}

# Build LangGraph StateGraph workflow
def build_graph():
    workflow = StateGraph(GraphState)
    
    workflow.add_node("extract_metrics", extract_metrics_node)
    workflow.add_node("completeness_check", completeness_check_node)
    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("multi_metric_reasoning", multi_metric_reasoning_node)
    workflow.add_node("recommendation_generator", recommendation_generator_node)
    workflow.add_node("format_output", format_output_node)
    
    workflow.set_entry_point("extract_metrics")
    workflow.add_edge("extract_metrics", "completeness_check")
    
    def route_after_check(state: GraphState):
        if state.get("is_complete", False):
            return "retrieve"
        else:
            return "format_output"
            
    workflow.add_conditional_edges(
        "completeness_check",
        route_after_check,
        {
            "retrieve": "retrieve",
            "format_output": "format_output"
        }
    )
    
    workflow.add_edge("retrieve", "multi_metric_reasoning")
    workflow.add_edge("multi_metric_reasoning", "recommendation_generator")
    workflow.add_edge("recommendation_generator", "format_output")
    workflow.add_edge("format_output", END)
    
    return workflow.compile()

app_graph = build_graph()
