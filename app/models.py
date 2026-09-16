import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import declarative_base, relationship
from pgvector.sqlalchemy import Vector
from app.config import settings

Base = declarative_base()

class KnowledgeChunk(Base):
    __tablename__ = "knowledge_chunks"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(50), nullable=False) # 'soil' | 'biodiversity' | 'climate' | 'land_use' | 'human_impact'
    source_title = Column(Text, nullable=False)
    source_url = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(settings.EMBEDDING_DIMENSION))

    recommendations = relationship("Recommendation", back_populates="source_chunk")

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    intervention = Column(Text, nullable=False)
    mechanism = Column(Text, nullable=False)
    impacted_metrics = Column(ARRAY(Text), nullable=False)
    expected_improvement = Column(Text, nullable=True)
    time_horizon = Column(String(20), nullable=True) # short | medium | long
    citation = Column(Text, nullable=False)
    source_chunk_id = Column(Integer, ForeignKey("knowledge_chunks.id"), nullable=True)

    source_chunk = relationship("KnowledgeChunk", back_populates="recommendations")

class Conversation(Base):
    __tablename__ = "conversations"

    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime, default=datetime.utcnow)

    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("conversations.session_id"), nullable=False)
    role = Column(String(10), nullable=False) # 'user' | 'assistant'
    content = Column(Text, nullable=False)
    extracted_metrics = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")
