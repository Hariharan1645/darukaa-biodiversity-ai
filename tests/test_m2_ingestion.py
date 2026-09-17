import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.ingestion import ingest_knowledge_base, load_and_parse_documents
from app.retrieval import retrieve_relevant_chunks

def test_document_parsing():
    """Verify loading and parsing of reference documents in data/sources."""
    sources_dir = os.path.join(os.path.dirname(__file__), "..", "data", "sources")
    chunks = load_and_parse_documents(sources_dir)
    assert len(chunks) >= 5, f"Expected at least 5 document chunks, got {len(chunks)}"
    
    categories = {c["category"] for c in chunks}
    print(f"\n[Parsed Categories]: {categories}")
    assert len(categories) >= 1, "Expected at least 1 category"
    assert categories.issubset({"soil", "climate", "biodiversity", "human_impact", "land_use"})

def test_ingestion_and_retrieval():
    """Verify ingestion pipeline execution and vector similarity retrieval."""
    accepted_chunks, _ = ingest_knowledge_base()
    assert len(accepted_chunks) >= 5, f"Expected at least 5 chunks ingested, got {len(accepted_chunks)}"
    
    # Perform test query
    query = "Soil organic carbon depletion and cover crops in low rainfall semi-arid farm"
    results = retrieve_relevant_chunks(query, top_k=3)
    
    assert len(results) > 0, "Retrieval returned 0 chunks."
    print(f"\n[Query]: '{query}'")
    for r in results:
        print(f"- Source: {r['source_title']} | Similarity: {r['similarity']:.4f} | Category: {r['category']}")
        assert "content" in r
        assert r["similarity"] > 0.3, f"Expected similarity > 0.3, got {r['similarity']}"

if __name__ == "__main__":
    print("Running document parsing test...")
    test_document_parsing()
    print("Running ingestion and retrieval test...")
    test_ingestion_and_retrieval()
    print("All M2 tests passed!")
