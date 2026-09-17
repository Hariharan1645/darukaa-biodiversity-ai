import os
import sys
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app

client = TestClient(app)

def test_chat_json_endpoint():
    """Verify POST /chat/json endpoint with complete structured metrics payload."""
    print("=" * 60)
    print("RUNNING STRUCTURED JSON INPUT TEST (M5)")
    print("=" * 60)
    
    payload = {
        "session_id": None,
        "metrics": {
            "soil_organic_carbon": 0.3,
            "rainfall": "low",
            "land_use": "monoculture wheat",
            "region_type": "semi-arid"
        }
    }
    
    print(f"\n[Sending POST /chat/json Payload]: {payload}")
    resp = client.post("/chat/json", json=payload)
    
    assert resp.status_code == 200, f"Expected status 200, got {resp.status_code}"
    data = resp.json()
    
    session_id = data["session_id"]
    reply_type = data["reply_type"]
    metrics = data["extracted_metrics"]
    recs = data["recommendations"]
    reasoning = data["reasoning_summary"]
    
    print(f"\n[Response Payload]:")
    print(f"Session ID: {session_id}")
    print(f"Reply Type: {reply_type}")
    print(f"Extracted Metrics: {metrics}")
    print(f"Recommendations Count: {len(recs) if recs else 0}")
    print(f"Reasoning Summary Length: {len(reasoning) if reasoning else 0}")
    
    assert session_id is not None
    assert reply_type == "recommendation", f"Expected 'recommendation', got {reply_type}"
    assert len(metrics) >= 4, f"Expected >= 4 metrics, got {len(metrics)}"
    assert recs and len(recs) >= 1, "Expected recommendations list"
    
    rec = recs[0]
    print("\n--- SAMPLE RECOMMENDATION ---")
    print(f"Intervention: {str(rec.get('intervention')).encode('ascii', 'ignore').decode('ascii')}")
    print(f"Mechanism: {str(rec.get('mechanism')).encode('ascii', 'ignore').decode('ascii')}")
    print(f"Impacted Metrics: {rec.get('impacted_metrics')}")
    print(f"Expected Improvement: {str(rec.get('expected_improvement')).encode('ascii', 'ignore').decode('ascii')}")
    print(f"Time Horizon: {rec.get('time_horizon')}")
    print(f"Citation: {str(rec.get('citation')).encode('ascii', 'ignore').decode('ascii')}")
    
    assert "intervention" in rec and rec["intervention"]
    assert "mechanism" in rec and rec["mechanism"]
    assert "citation" in rec and rec["citation"]
    
    print("\n" + "=" * 60)
    print("ALL M5 STRUCTURED JSON INPUT TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    test_chat_json_endpoint()
