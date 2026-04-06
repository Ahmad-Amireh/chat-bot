import json
import requests
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.chat_session import ChatSession
from app.models.message import Message
from app.schemas.message import MessageCreate
from app.services.message import create_message, list_messages_for_session
from app.services.memory import update_session_summary
from app.models.user import User
from groq import Groq
from app.core.config import settings
from fastmcp import Client
import asyncio



client = Groq(api_key=settings.GROK_API_KEY)

# -----------------------------
# MCP TOOLS
# -----------------------------
MCP_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_products",
            "description": "List all products with their prices",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_product",
            "description": "Add a new product",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "price": {"type": "number"}
                },
                "required": ["name", "price"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_product",
            "description": "Update product",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "integer"},
                    "name": {"type": "string"},
                    "price": {"type": "number"}
                },
                "required": ["product_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_product",
            "description": "Delete product",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "integer"}
                },
                "required": ["product_id"]
            }
        }
    }
]


# -----------------------------
# MCP CALL FUNCTION
# -----------------------------
import requests

def call_mcp_tool(name: str, args: dict):

    async def _call():
        client = Client("http://127.0.0.1:8000/mcp")

        async with client:
            result = await client.call_tool(name, args)

            # 🔥 THIS is the correct field
            data = result.structured_content
            print(data)
            if isinstance(data, dict) and "result" in data:
                return data["result"]

            return data

    return asyncio.run(_call())
# -----------------------------
# MAIN FUNCTION
# -----------------------------
def chat_with_llama_client(db: Session, user: User, session_id: int, user_content: str) -> Message:

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

    # 2️⃣ Get session
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # 3️⃣ Load messages
    session_messages = list_messages_for_session(db, user, session_id)

    prompt_messages = []

    # Summary memory
    if session.summary:
        prompt_messages.append({
            "role": "system",
            "content": f"Conversation summary: {session.summary}"
        })

    # Short-term memory
    recent_messages = (
        session_messages if not session.summary
        else session_messages[-settings.SHORT_TERM_MEMORY:]
    )

    prompt_messages += [
        {"role": m.role, "content": m.content}
        for m in recent_messages
    ]

    # Add current user message
    prompt_messages.append({"role": "user", "content": user_content})

    # -----------------------------
    # 4️⃣ FIRST CALL (tool detection)
    # -----------------------------
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=prompt_messages,
        tools=MCP_TOOLS,
        tool_choice="auto",
        max_tokens=500
    )

    assistant_message = response.choices[0].message

    # -----------------------------
    # 5️⃣ HANDLE TOOL CALLS
    # -----------------------------
    if assistant_message.tool_calls:
        prompt_messages.append(assistant_message)

        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            tool_result = call_mcp_tool(tool_name, tool_args)
            print(f"tool_result: {tool_result}")

            prompt_messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(tool_result)
            })

        # -----------------------------
        # 6️⃣ SECOND CALL (final answer)
        # -----------------------------
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=prompt_messages,
            max_tokens=500
        )

        assistant_message = response.choices[0].message

    assistant_content = assistant_message.content

    # 7️⃣ Store assistant message
    assistant_msg = create_message(
        db,
        user,
        MessageCreate(
            session_id=session_id,
            role="assistant",
            content=assistant_content
        )
    )

    # 8️⃣ Update memory
    update_session_summary(db, user, session_id)

    return assistant_msg