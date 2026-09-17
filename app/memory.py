import uuid
import logging
from typing import Dict, Any, Optional, List
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models import Conversation, Message

logger = logging.getLogger(__name__)

# In-memory session store fallback for offline execution
_MEMORY_CACHE: Dict[str, Dict[str, Any]] = {}

def get_or_create_session_id(session_id: Optional[str] = None) -> str:
    """Validate or generate a new session UUID."""
    if session_id:
        try:
            val = uuid.UUID(session_id)
            return str(val)
        except ValueError:
            pass
    return str(uuid.uuid4())

def load_session_state(session_id: str) -> Dict[str, Any]:
    """Load accumulated metrics and message history for a session."""
    session_id = get_or_create_session_id(session_id)
    
    # 1. Try DB first
    try:
        engine = create_engine(settings.DATABASE_URL, connect_args={"connect_timeout": 2})
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        conv = db_session.query(Conversation).filter(Conversation.session_id == session_id).first()
        if conv and conv.messages:
            accumulated_metrics = {}
            history = []
            for msg in conv.messages:
                history.append({"role": msg.role, "content": msg.content})
                if msg.extracted_metrics:
                    for k, v in msg.extracted_metrics.items():
                        if v is not None and v != "":
                            accumulated_metrics[k] = v
            db_session.close()
            logger.info(f"Loaded session {session_id} from DB with {len(history)} messages and {len(accumulated_metrics)} metrics.")
            return {"session_id": session_id, "extracted_metrics": accumulated_metrics, "history": history}
        db_session.close()
    except Exception as e:
        logger.debug(f"Database session load note: {e}")

    # 2. Fallback to in-memory cache
    if session_id in _MEMORY_CACHE:
        logger.info(f"Loaded session {session_id} from in-memory cache.")
        return _MEMORY_CACHE[session_id]
        
    initial_state = {
        "session_id": session_id,
        "extracted_metrics": {},
        "history": []
    }
    _MEMORY_CACHE[session_id] = initial_state
    return initial_state

def save_session_turn(session_id: str, user_message: str, assistant_response: Dict[str, Any], accumulated_metrics: Dict[str, Any]):
    """Persist turn messages and accumulated metrics."""
    session_id = get_or_create_session_id(session_id)
    
    # Update in-memory cache
    if session_id not in _MEMORY_CACHE:
        _MEMORY_CACHE[session_id] = {"session_id": session_id, "extracted_metrics": {}, "history": []}
        
    _MEMORY_CACHE[session_id]["extracted_metrics"] = accumulated_metrics
    _MEMORY_CACHE[session_id]["history"].append({"role": "user", "content": user_message})
    
    reply_msg = assistant_response.get("message", "")
    if not reply_msg and assistant_response.get("recommendations"):
        reply_msg = f"Generated {len(assistant_response['recommendations'])} recommendations."
    _MEMORY_CACHE[session_id]["history"].append({"role": "assistant", "content": reply_msg})
    
    # Try DB save
    try:
        engine = create_engine(settings.DATABASE_URL, connect_args={"connect_timeout": 2})
        Session = sessionmaker(bind=engine)
        db_session = Session()
        
        conv = db_session.query(Conversation).filter(Conversation.session_id == session_id).first()
        if not conv:
            conv = Conversation(session_id=uuid.UUID(session_id))
            db_session.add(conv)
            db_session.commit()
            
        user_msg_obj = Message(
            session_id=uuid.UUID(session_id),
            role="user",
            content=user_message,
            extracted_metrics=accumulated_metrics
        )
        assistant_msg_obj = Message(
            session_id=uuid.UUID(session_id),
            role="assistant",
            content=reply_msg,
            extracted_metrics=accumulated_metrics
        )
        db_session.add(user_msg_obj)
        db_session.add(assistant_msg_obj)
        db_session.commit()
        db_session.close()
        logger.info(f"Saved session turn to database for session {session_id}.")
    except Exception as e:
        logger.debug(f"Database session save note ({e}); turn persisted to in-memory session store.")
