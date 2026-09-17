import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.validator import verify_and_sanitize_recommendations, RecommendationSchema

def test_anti_hallucination_citation_replacement():
    """Verify that hallucinated citations are caught and replaced with grounded source titles."""
    print("=" * 60)
    print("RUNNING ANTI-HALLUCINATION CITATION VERIFICATION TEST (M6)")
    print("=" * 60)
    
    retrieved_chunks = [
        {
            "source_title": "Food and Agriculture Organization (FAO) - Technical Manual on Soil Organic Carbon Management",
            "category": "soil"
        }
    ]
    
    hallucinated_input = [
        {
            "intervention": "Apply Bio-char soil amendment",
            "mechanism": "Increases cation exchange capacity and long-term carbon storage.",
            "impacted_metrics": ["soil_organic_carbon"],
            "expected_improvement": "+2 tonnes C/ha",
            "time_horizon": "medium term", # Needs enum sanitization
            "citation": "Fake Journal of Unverified Studies 2025", # Hallucinated citation!
            "confidence": "high"
        }
    ]
    
    sanitized = verify_and_sanitize_recommendations(hallucinated_input, retrieved_chunks)
    
    rec = sanitized[0]
    print(f"\n[Hallucinated Input Citation]: 'Fake Journal of Unverified Studies 2025'")
    print(f"[Sanitized Grounded Citation]: '{rec['citation']}'")
    print(f"[Sanitized Time Horizon Enum]: '{rec['time_horizon']}'")
    print(f"[Sanitized Impacted Metrics]: {rec['impacted_metrics']}")
    
    # Assert anti-hallucination replacement
    assert rec["citation"] == retrieved_chunks[0]["source_title"]
    assert rec["time_horizon"] in ["short", "medium", "long"]
    assert len(rec["impacted_metrics"]) >= 2
    
    # Verify Pydantic schema validation
    schema_obj = RecommendationSchema(**rec)
    assert schema_obj.citation == retrieved_chunks[0]["source_title"]
    
    print("\n" + "=" * 60)
    print("ALL M6 OUTPUT ENFORCEMENT & CITATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    test_anti_hallucination_citation_replacement()
