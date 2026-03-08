from sqlalchemy.orm import Session
from app.models.chat_session import ChatSession
from app.models.message import Message
from app.services.message import list_messages_for_session
from app.core.config import settings
from groq import Groq
from app.core.config import settings

client = Groq(api_key=settings.GROK_API_KEY)


def summarize_messages(messages: list[Message]) -> str:
    """
    Summarize a list of messages into a compact conversation memory.
    Always returns a single concise paragraph without repetition.
    """
    conversation = "\n".join(f"{m.role}: {m.content}" for m in messages)

    prompt = f"""
    Summarize the following conversation in **one concise paragraph**.
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


def update_session_summary(db: Session, session_id: int):
    """
    Update the session summary by summarizing older messages.
    Overwrites the existing summary instead of appending.
    """
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        return

    messages = list_messages_for_session(db, session_id)

    # Do nothing if conversation is too short
    if len(messages) < settings.SUMMARY_TRIGGER:
        return

    # Summarize all except last SHORT_TERM_MEMORY messages
    messages_to_summarize = messages[:-settings.SHORT_TERM_MEMORY]

    if not messages_to_summarize:
        return  # nothing to summarize

    # Combine old summary + new messages
    combined_text = ""
    if session.summary:
        combined_text += session.summary + "\n"

    combined_text += "\n".join(f"{m.role}: {m.content}" for m in messages_to_summarize)

    # Summarize combined text
    # We create a temporary Message object for the summarizer
    new_summary = summarize_messages([Message(role="system", content=combined_text)])

    # Overwrite summary in DB
    session.summary = new_summary
    db.commit()