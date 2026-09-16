import os
import sys
from collections import Counter

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.ingestion import ingest_knowledge_base
from app.retrieval import retrieve_relevant_chunks

def run_m2_5_verification():
    print("=" * 60)
    print("RUNNING MILESTONE 2.5 KNOWLEDGE BASE EXPANSION INGESTION")
    print("=" * 60)
    
    accepted_chunks, skipped_log = ingest_knowledge_base()
    
    print(f"\n[Ingestion Summary]:")
    print(f"- Total Unique Chunks Ingested: {len(accepted_chunks)}")
    print(f"- Total Chunks Skipped for Redundancy: {len(skipped_log)}")
    
    # Category & Biome Breakdown
    categories = Counter(c.get("category", "general") for c in accepted_chunks)
    biomes = Counter(c.get("biome", "temperate") for c in accepted_chunks)
    confidences = Counter(c.get("confidence", "high_evidence") for c in accepted_chunks)
    
    print("\n--- CATEGORY BREAKDOWN ---")
    for cat, count in categories.items():
        print(f"  * {cat}: {count} chunks")
        
    print("\n--- BIOME / SCENARIO BREAKDOWN ---")
    for b, count in biomes.items():
        print(f"  * {b}: {count} chunks")

    print("\n--- CONFIDENCE BREAKDOWN ---")
    for conf, count in confidences.items():
        print(f"  * {conf}: {count} chunks")
        
    print("\n" + "=" * 60)
    print("RUNNING SPOT-CHECK RETRIEVAL QUERIES (NEW SCENARIOS)")
    print("=" * 60)
    
    spot_queries = [
        "tropical agroforestry land with declining pollinators",
        "urban green space with compacted soil",
        "nitrogen over-application in intensive cropland"
    ]
    
    spot_check_results = []
    
    for q in spot_queries:
        print(f"\n[QUERY]: '{q}'")
        results = retrieve_relevant_chunks(q, top_k=3)
        query_res = {"query": q, "top_matches": []}
        for i, r in enumerate(results, 1):
            source_title = r.get("source_title", "Reference").encode("ascii", "ignore").decode("ascii")
            sim = r.get("similarity", 0.0)
            category = r.get("category", "general")
            snippet = r.get("content", "")[:120].replace("\n", " ").encode("ascii", "ignore").decode("ascii")
            print(f"  Rank {i}: {source_title} (Category: {category}, Sim: {sim:.4f})")
            print(f"    Snippet: {snippet}...")
            query_res["top_matches"].append({
                "rank": i,
                "title": source_title,
                "similarity": sim,
                "category": category
            })
        spot_check_results.append(query_res)
        
    return accepted_chunks, skipped_log, categories, biomes, spot_check_results

if __name__ == "__main__":
    run_m2_5_verification()
