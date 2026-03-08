from sqlalchemy.orm import Session
from app.models.message import Message
from app.services.message import create_message, list_messages_for_session
from groq import Groq
from app.core.config import settings
from app.schemas.message import MessageCreate
from app.models.chat_session import ChatSession
from app.services.memory import update_session_summary



client = Groq(api_key=settings.GROK_API_KEY)

def chat_with_llama_client(db: Session, session_id: int, user_content: str):

    # 1️⃣ store user message
    user_msg = create_message(
        db,
        MessageCreate(
            session_id=session_id,
            role="user",
            content=user_content
        )
    )

    # 2️⃣ get session + messages
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    session_messages = list_messages_for_session(db, session_id)

    prompt_messages = []

    # 3️⃣ add summary memory
    if session.summary:
        prompt_messages.append({
            "role": "system",
            "content": f"Conversation summary: {session.summary}"
        })

    # 4️⃣ add recent messages only
    recent_messages = session_messages[settings.SHORT_TERM_MEMORY:]

    prompt_messages += [
        {"role": m.role, "content": m.content}
        for m in recent_messages
    ]

    # 5️⃣ call model
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=prompt_messages,
        max_tokens=500
    )

    assistant_content = response.choices[0].message.content

    # 6️⃣ store assistant response
    assistant_msg = create_message(
        db,
        MessageCreate(
            session_id=session_id,
            role="assistant",
            content=assistant_content
        )
    )

    # 7️⃣ update summary if needed
    update_session_summary(db, session_id)

    return assistant_msg