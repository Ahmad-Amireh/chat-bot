from groq import Groq
from app.core.config import settings
from app.models.message import Message

client = Groq(api_key=settings.GROK_API_KEY)


def summarize_messages(messages: list[Message]) -> str:
    """
    Summarize a list of messages into a compact conversation memory.
    """

    conversation = "\n".join(
        f"{m.role}: {m.content}" for m in messages
    )

    prompt = f"""
    Summarize the following conversation **in one concise paragraph**.
    Include only key facts, goals, and context.
    Do not repeat the same fact multiple times.
    Focus on information that will help the assistant remember the user.

    Conversation:
    {conversation}

    Summary:
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200
    )

    return response.choices[0].message.content


from sqlalchemy.orm import Session
from app.models.chat_session import ChatSession
from app.services.message import list_messages_for_session
from app.services.memory import summarize_messages



def update_session_summary(db: Session, session_id: int):

    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()

    if not session:
        return

    messages = list_messages_for_session(db, session_id)

    # if conversation still small → do nothing
    if len(messages) < settings.SUMMARY_TRIGGER:
        return

    # take older messages to summarize
    messages_to_summarize = messages[:settings.SUMMARY_CHUNK]

    new_summary = summarize_messages(messages_to_summarize)

    if session.summary:
        session.summary = session.summary + "\n" + new_summary
    else:
        session.summary = new_summary

    db.commit()