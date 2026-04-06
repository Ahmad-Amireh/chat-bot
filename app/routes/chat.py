from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.llm.llama import chat_with_llama_client, call_mcp_tool
from app.schemas.chat import ChatRequest, ChatResponse, ExecuteRequest, ExecuteResponse
from app.services.auth import CurrentUser
from app.models.pending_action import PendingAction
from app.models.chat_session import ChatSession
from app.models.message import Message
from app.schemas.message import MessageCreate
from app.services.message import create_message
from fastapi import HTTPException
import json

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/message", response_model=ChatResponse)
def send_message(request: ChatRequest, user: CurrentUser, db: Session = Depends(get_db)):
    result = chat_with_llama_client(db, user, request.session_id, request.message)
    return ChatResponse(
        content=result["content"],
        requires_confirmation=result["requires_confirmation"],
        action_id=result.get("action_id")
    )


@router.post("/execute", response_model=ExecuteResponse)
def execute_action(request: ExecuteRequest, user: CurrentUser, db: Session = Depends(get_db)):

    # 1️⃣ Fetch pending action
    pending = db.get(PendingAction, request.action_id)
    if not pending:
        raise HTTPException(status_code=404, detail="Action not found or already executed")

    # 2️⃣ Validate session belongs to current user
    session = db.get(ChatSession, pending.session_id)
    if not session or session.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # 3️⃣ Delete pending — one time use regardless of confirm/cancel
    db.delete(pending)

    if not request.confirmed:
        create_message(db, user, MessageCreate(
            session_id=pending.session_id,
            role="assistant",
            content="Action cancelled."
        ))
        db.commit()
        return ExecuteResponse(content="Action cancelled.")

    # 4️⃣ Execute MCP tool
    tool_args = json.loads(pending.tool_args)
    tool_result = call_mcp_tool(pending.tool_name, tool_args)

    result_text = json.dumps(tool_result)

    # 5️⃣ Save result as assistant message
    create_message(db, user, MessageCreate(
        session_id=pending.session_id,
        role="assistant",
        content=result_text
    ))
    db.commit()

    return ExecuteResponse(content=result_text)