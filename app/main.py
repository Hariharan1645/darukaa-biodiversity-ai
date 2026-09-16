from fastapi import FastAPI
from app.config import settings

app = FastAPI(
    title="Darukaa.Earth Biodiversity Intelligence AI",
    description="RAG-based AI Environmental Scientist for biodiversity and ecological recommendations.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "Darukaa Biodiversity AI Chatbot",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "groq_model": settings.GROQ_MODEL_NAME,
        "embedding_model": settings.EMBEDDING_MODEL_NAME
    }
