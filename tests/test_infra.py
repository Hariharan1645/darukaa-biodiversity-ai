import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.config import settings

@pytest.mark.skipif(not settings.GROQ_API_KEY, reason="GROQ_API_KEY environment variable is not set")
def test_groq_api_connection():
    """Verify Groq API key and model connectivity using langchain-groq."""
    from langchain_groq import ChatGroq
    
    assert settings.GROQ_API_KEY, "GROQ_API_KEY is not set in environment."
    llm = ChatGroq(
        groq_api_key=settings.GROQ_API_KEY,
        model_name=settings.GROQ_MODEL_NAME,
        temperature=0
    )
    
    response = llm.invoke("Hello! Reply with 'Groq connected successfully.' if you receive this.")
    print("\n[Groq Response]:", response.content)
    assert response.content, "Groq returned empty response."

def test_local_embeddings():
    """Verify local HuggingFace / SentenceTransformers embeddings."""
    from sentence_transformers import SentenceTransformer
    
    model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
    embedding = model.encode("Soil organic carbon content in degraded semi-arid lands.")
    
    print(f"\n[Embedding generated]: shape = {embedding.shape}")
    assert len(embedding) == settings.EMBEDDING_DIMENSION, f"Expected dim {settings.EMBEDDING_DIMENSION}, got {len(embedding)}"

if __name__ == "__main__":
    print("Testing Groq API Connection...")
    test_groq_api_connection()
    print("Testing Local Embeddings...")
    test_local_embeddings()
    print("All basic infrastructure tests passed!")
