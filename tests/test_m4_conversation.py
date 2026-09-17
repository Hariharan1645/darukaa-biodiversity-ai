import os
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from app.memory import load_session_state

client = TestClient(app)

def test_multi_turn_conversation_flow():
    """Verify multi-turn session memory, metric accumulation, and clarifying question routing."""
    print("=" * 60)
    print("RUNNING MULTI-TURN CONVERSATIONAL TEST (M4)")
    print("=" * 60)
    
    # -------------------------------------------------------------
    # TURN 1: Incomplete Input (Metrics = 1 < 3)
    # -------------------------------------------------------------
    print("\n--- TURN 1: Sending incomplete prompt ('Biodiversity is declining on my land.') ---")
    req1 = {"session_id": None, "message": "Biodiversity is declining on my land."}
    resp1 = client.post("/chat", json=req1)
    
    assert resp1.status_code == 200, f"Turn 1 status code {resp1.status_code}"
    data1 = resp1.json()
    
    session_id = data1["session_id"]
    reply_type1 = data1["reply_type"]
    metrics1 = data1["extracted_metrics"]
    question1 = data1["message"]
    
    print(f"Session ID: {session_id}")
    print(f"Reply Type: {reply_type1}")
    print(f"Extracted Metrics Turn 1: {metrics1}")
    print(f"Clarifying Question: {question1}")
    
    assert session_id is not None
    assert reply_type1 == "clarifying_question", f"Expected 'clarifying_question', got {reply_type1}"
    assert question1 is not None and len(question1) > 10
    assert len(metrics1) < 3, f"Expected < 3 metrics in Turn 1, got {len(metrics1)}"
    
    # -------------------------------------------------------------
    # TURN 2: Responding with missing metrics (Accumulated >= 3)
    # -------------------------------------------------------------
    print("\n--- TURN 2: Responding with additional metrics ---")
    req2 = {
        "session_id": session_id,
        "message": "Soil organic carbon is 0.3%, rainfall is low, and I grow monoculture wheat in a semi-arid region."
    }
    resp2 = client.post("/chat", json=req2)
    
    assert resp2.status_code == 200, f"Turn 2 status code {resp2.status_code}"
    data2 = resp2.json()
    
    reply_type2 = data2["reply_type"]
    metrics2 = data2["extracted_metrics"]
    recs2 = data2["recommendations"]
    reasoning2 = data2["reasoning_summary"]
    
    print(f"Reply Type Turn 2: {reply_type2}")
    print(f"Accumulated Metrics Turn 2: {metrics2}")
    print(f"Recommendations Count: {len(recs2) if recs2 else 0}")
    
    assert data2["session_id"] == session_id, "Session ID changed across turns"
    assert reply_type2 == "recommendation", f"Expected 'recommendation', got {reply_type2}"
    assert len(metrics2) >= 3, f"Expected >= 3 metrics in Turn 2, got {len(metrics2)}"
    assert recs2 and len(recs2) >= 1, "Expected recommendations in Turn 2"
    assert reasoning2 is not None and len(reasoning2) > 20
    
    # Verify mandatory schema in recommendation
    rec = recs2[0]
    assert "intervention" in rec and rec["intervention"]
    assert "mechanism" in rec and rec["mechanism"]
    assert "citation" in rec and rec["citation"]
    
    # -------------------------------------------------------------
    # TURN 3: Verification of Session State Memory Persistence
    # -------------------------------------------------------------
    print("\n--- TURN 3: Verifying session state memory persistence ---")
    state3 = load_session_state(session_id)
    history3 = state3["history"]
    metrics3 = state3["extracted_metrics"]
    
    print(f"Persisted Messages in Session History: {len(history3)}")
    print(f"Persisted Metrics in Session State: {metrics3}")
    
    assert len(history3) >= 4, f"Expected at least 4 messages in session history (2 turns), got {len(history3)}"
    assert len(metrics3) >= 3, "Persisted state metrics missing in session store"
    
    print("\n" + "=" * 60)
    print("ALL M4 MULTI-TURN CONVERSATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    test_multi_turn_conversation_flow()
