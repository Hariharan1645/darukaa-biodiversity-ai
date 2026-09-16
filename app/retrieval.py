import os
import json
import logging
import numpy as np
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models import KnowledgeChunk, Recommendation

logger = logging.getLogger(__name__)

# Global singleton embedding model to avoid reloading weights repeatedly
_model_instance = None

def get_embedding_model() -> SentenceTransformer:
    global _model_instance
    if _model_instance is None:
        logger.info(f"Loading embedding model for retrieval: {settings.EMBEDDING_MODEL_NAME}")
        _model_instance = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
    return _model_instance

def cosine_similarity(v1: np.ndarray, v2: np.ndarray) -> float:
    """Calculate cosine similarity between two 1D vectors."""
    dot_product = np.dot(v1, v2)
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0
    return float(dot_product / (norm_v1 * norm_v2))

def retrieve_relevant_chunks(query: str, top_k: int = 4) -> List[Dict[str, Any]]:
    """Retrieve top-k relevant knowledge chunks using vector similarity search."""
    model = get_embedding_model()
    query_vec = model.encode(query, show_progress_bar=False)
    
    # 1. Try DB pgvector similarity search first
    try:
        engine = create_engine(settings.DATABASE_URL, connect_args={"connect_timeout": 2})
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Using pgvector cosine distance operator <=> or L2 distance
        # Querying KnowledgeChunk with ordering by cosine distance
        query_vector_str = "[" + ",".join(map(str, query_vec.tolist())) + "]"
        sql = text(f"""
            SELECT id, category, source_title, source_url, content,
                   1 - (embedding <=> '{query_vector_str}'::vector) AS similarity
            FROM knowledge_chunks
            ORDER BY embedding <=> '{query_vector_str}'::vector ASC
            LIMIT {top_k};
        """)
        
        results = session.execute(sql).fetchall()
        session.close()
        
        if results:
            retrieved = []
            for r in results:
                retrieved.append({
                    "id": r[0],
                    "category": r[1],
                    "source_title": r[2],
                    "source_url": r[3],
                    "content": r[4],
                    "similarity": float(r[5])
                })
            logger.info(f"Retrieved {len(retrieved)} chunks from pgvector database.")
            return retrieved
    except Exception as e:
        logger.debug(f"DB pgvector retrieval unavailable ({e}); falling back to vector cache.")

    # 2. Fallback: Search local vector cache
    cache_path = os.path.join(os.path.dirname(__file__), "..", "data", "knowledge_cache.json")
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            chunks = json.load(f)
            
        scored_chunks = []
        for c in chunks:
            sim = cosine_similarity(query_vec, np.array(c["embedding"]))
            scored_chunks.append({
                "id": c.get("chunk_id", 0),
                "category": c.get("category", "general"),
                "source_title": c.get("title", "Reference"),
                "source_url": c.get("url", ""),
                "content": c.get("content", ""),
                "similarity": sim
            })
            
        scored_chunks.sort(key=lambda x: x["similarity"], reverse=True)
        top_chunks = scored_chunks[:top_k]
        logger.info(f"Retrieved {len(top_chunks)} chunks from local vector cache.")
        return top_chunks

    logger.warning("No knowledge base chunks found. Run app/ingestion.py first.")
    return []

if __name__ == "__main__":
    test_query = "Low soil organic carbon and low rainfall in semi-arid wheat monoculture"
    results = retrieve_relevant_chunks(test_query, top_k=3)
    print(f"\nSearch results for: '{test_query}'\n")
    for r in results:
        print(f"Title: {r['source_title']} (Category: {r['category']}, Similarity: {r['similarity']:.4f})")
        print(f"Content: {r['content'][:150]}...\n")
