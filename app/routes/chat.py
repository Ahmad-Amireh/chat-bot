from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.llm.llama import chat_with_llama_client
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("/message", response_model=ChatResponse)
def send_message(request: ChatRequest, db: Session = Depends(get_db)):
    assistant_msg = chat_with_llama_client(db, request.session_id, request.message)
    return ChatResponse(content=assistant_msg.content)