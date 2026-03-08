from sqlalchemy.orm import Session
from app.models.message import Message
from app.services.message import create_message, list_messages_for_session
from groq import Groq
from app.core.config import settings
from app.schemas.message import MessageCreate



client = Groq(api_key=settings.GROK_API_KEY)

def chat_with_llama_client(db: Session, session_id: int, user_content: str) -> Message:
    # 1️⃣ Store user message
    user_msg = create_message(
        db,
        message_data=MessageCreate(
            session_id=session_id,
            role="user",
            content=user_content
        )
    )

    # 2️⃣ Fetch previous messages (memory)
    session_messages = list_messages_for_session(db, session_id)
    prompt_messages = [{"role": m.role, "content": m.content} for m in session_messages]

    # 3️⃣ Call Qrok LLaMA via client
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=prompt_messages,
        max_tokens=500
    )

    assistant_content = response.choices[0].message.content

    # 4️⃣ Store assistant message
    assistant_msg = create_message(
        db,
        message_data=MessageCreate(
            session_id=session_id,
            role="assistant",
            content=assistant_content
        )
    )

    return assistant_msg