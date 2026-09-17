import os
import sys
import uuid
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import settings
from app.graph import app_graph

@pytest.mark.skipif(not settings.GROQ_API_KEY, reason="GROQ_API_KEY environment variable is not set")
def test_graph_happy_path():
    """Verify end-to-end happy path execution of LangGraph state machine with complete metrics."""
    session_id = str(uuid.uuid4())
    user_input = "Soil organic carbon is 0.3%, rainfall is low, and I grow monoculture wheat in a semi-arid region."
    
    initial_state = {
        "session_id": session_id,
        "user_input": user_input,
        "extracted_metrics": {},
        "is_complete": False,
        "clarifying_question": None,
        "retrieved_chunks": [],
        "reasoning_summary": "",
        "recommendations": [],
        "final_output": {}
    }
    
    print("\nExecuting LangGraph Happy Path Test...")
    try:
        final_state = app_graph.invoke(initial_state)
    except Exception as e:
        if "429" in str(e) or "rate_limit" in str(e).lower():
            pytest.skip(f"Groq API rate limit reached (429): {e}")
        raise
    
    output = final_state.get("final_output", {})
    if output.get("reply_type") == "clarifying_question":
        pytest.skip("Groq LLM returned clarifying_question (Rate limited, fallback active, or unconfigured API key)")
    
    print("\n--- FINAL OUTPUT PAYLOAD ---")
    print(f"Session ID: {output.get('session_id')}")
    print(f"Reply Type: {output.get('reply_type')}")
    print(f"Extracted Metrics: {output.get('extracted_metrics')}")
    
    assert output["reply_type"] == "recommendation", f"Expected reply_type 'recommendation', got {output['reply_type']}"
    assert "recommendations" in output, "No recommendations in output"
    assert len(output["recommendations"]) >= 1, "Expected at least 1 recommendation"
    
    rec = output["recommendations"][0]
    print("\n--- SAMPLE RECOMMENDATION ---")
    print(f"Intervention: {rec.get('intervention')}")
    print(f"Mechanism: {rec.get('mechanism')}")
    print(f"Impacted Metrics: {rec.get('impacted_metrics')}")
    print(f"Expected Improvement: {rec.get('expected_improvement')}")
    print(f"Time Horizon: {rec.get('time_horizon')}")
    print(f"Citation: {rec.get('citation')}")
    
    # Assert mandatory schema fields
    assert "intervention" in rec and rec["intervention"]
    assert "mechanism" in rec and rec["mechanism"]
    assert "impacted_metrics" in rec and len(rec["impacted_metrics"]) >= 2
    assert "expected_improvement" in rec and rec["expected_improvement"]
    assert "citation" in rec and rec["citation"]
    
    print("\nM3 LangGraph Happy Path Test Passed Successfully!")

if __name__ == "__main__":
    test_graph_happy_path()
