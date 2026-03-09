from sqlalchemy.orm import Session
from app.models.chat_session import ChatSession
from app.models.message import Message
from app.schemas.message import MessageCreate
from app.services.message import create_message, list_messages_for_session
from app.services.memory import update_session_summary
from groq import Groq
from app.core.config import settings
from fastapi import HTTPException
from app.models.user import User

client = Groq(api_key=settings.GROK_API_KEY)


def chat_with_llama_client(db: Session, user: User, session_id: int, user_content: str) -> Message:
    """
    Handle a user message, send to LLaMA, store response, and update summary.
    """
    print(user)
    # 1️⃣ Store user message
    user_msg = create_message(
        db,
        user,
        MessageCreate(
            session_id=session_id,
            role="user",
            content=user_content
        )
    )

    # 2️⃣ Get session and all messages
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    session_messages = list_messages_for_session(db, user, session_id)

    # 3️⃣ Build prompt for LLaMA
    prompt_messages = []

    # Add session summary as system message if exists
    if session.summary:
        prompt_messages.append({
            "role": "system",
            "content": f"Conversation summary: {session.summary}"
        })
    
    if not session.summary:
        recent_messages = session_messages
    else:
        recent_messages = session_messages[-settings.SHORT_TERM_MEMORY:]

    prompt_messages += [
        {"role": m.role, "content": m.content} for m in recent_messages
    ]

    # 4️⃣ Call LLaMA model via Groq
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=prompt_messages,
        max_tokens=500
    )

    assistant_content = response.choices[0].message.content

    # 5️⃣ Store assistant message
    assistant_msg = create_message(
        db,
        user,
        MessageCreate(
            session_id=session_id,
            role="assistant",
            content=assistant_content
        )
    )
    print(prompt_messages)
    # 6️⃣ Update session summary if needed
    update_session_summary(db, user, session_id)

    return assistant_msg