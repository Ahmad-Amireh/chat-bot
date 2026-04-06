# app/services/llm/llama.py
import json
import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.chat_session import ChatSession
from app.models.message import Message
from app.models.pending_action import PendingAction
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
# CONFIRMATION TOOLS
# -----------------------------
CONFIRMATION_TOOLS = {"add_product", "update_product", "delete_product"}

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
# MCP CALL
# -----------------------------
def call_mcp_tool(name: str, args: dict):
    async def _call():
        mcp_client = Client("http://127.0.0.1:8000/mcp")
        async with mcp_client:
            result = await mcp_client.call_tool(name, args)
            data = result.structured_content
            if isinstance(data, dict) and "result" in data:
                return data["result"]
            return data
    return asyncio.run(_call())

# -----------------------------
# CONFIRMATION TEXT
# -----------------------------
def build_confirmation_text(tool_name: str, tool_args: dict) -> str:
    if tool_name == "delete_product":
        return f"Are you sure you want to delete product ID **{tool_args.get('product_id')}**? Click **Confirm** or **Cancel**."
    elif tool_name == "add_product":
        return f"Add **{tool_args.get('name')}** for **${tool_args.get('price')}**? Click **Confirm** or **Cancel**."
    elif tool_name == "update_product":
        changes = []
        if tool_args.get("name"):
            changes.append(f"name → {tool_args['name']}")
        if tool_args.get("price"):
            changes.append(f"price → ${tool_args['price']}")
        return f"Update product ID **{tool_args.get('product_id')}** ({', '.join(changes)})? Click **Confirm** or **Cancel**."
    return "Confirm this action? Click **Confirm** or **Cancel**."

# -----------------------------
# MAIN FUNCTION
# -----------------------------
def chat_with_llama_client(db: Session, user: User, session_id: int, user_content: str) -> dict:

    # 1️⃣ Store user message
    create_message(
        db, user,
        MessageCreate(session_id=session_id, role="user", content=user_content)
    )

    # 2️⃣ Get + validate session
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if session.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # 3️⃣ Build prompt messages
    session_messages = list_messages_for_session(db, user, session_id)
    prompt_messages = []

    if session.summary:
        prompt_messages.append({
            "role": "system",
            "content": f"Conversation summary: {session.summary}"
        })

    recent_messages = (
        session_messages if not session.summary
        else session_messages[-settings.SHORT_TERM_MEMORY:]
    )
    prompt_messages += [{"role": m.role, "content": m.content} for m in recent_messages]
    prompt_messages.append({"role": "user", "content": user_content})

    # 4️⃣ First LLM call
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=prompt_messages,
        tools=MCP_TOOLS,
        tool_choice="auto",
        max_tokens=500
    )

    assistant_message = response.choices[0].message

    # 5️⃣ Handle tool calls
    if assistant_message.tool_calls:
        tool_call = assistant_message.tool_calls[0]
        tool_name = tool_call.function.name
        tool_args = json.loads(tool_call.function.arguments)

        # ✅ Needs confirmation — store in DB and return early
        if tool_name in CONFIRMATION_TOOLS:
            action_id = str(uuid.uuid4())

            pending = PendingAction(
                id=action_id,
                session_id=session_id,
                tool_name=tool_name,
                tool_args=json.dumps(tool_args)
            )
            db.add(pending)

            confirmation_text = build_confirmation_text(tool_name, tool_args)

            create_message(
                db, user,
                MessageCreate(session_id=session_id, role="assistant", content=confirmation_text)
            )

            db.commit()

            return {
                "content": confirmation_text,
                "requires_confirmation": True,
                "action_id": action_id
            }

        # ✅ No confirmation needed (list_products) — execute immediately
        prompt_messages.append(assistant_message)
        tool_result = call_mcp_tool(tool_name, tool_args)

        prompt_messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(tool_result)
        })

        # 6️⃣ Second LLM call
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=prompt_messages,
            max_tokens=500
        )
        assistant_message = response.choices[0].message

    assistant_content = assistant_message.content

    # 7️⃣ Store assistant message
    create_message(
        db, user,
        MessageCreate(session_id=session_id, role="assistant", content=assistant_content)
    )

    # 8️⃣ Update memory
    update_session_summary(db, user, session_id)

    return {
        "content": assistant_content,
        "requires_confirmation": False,
        "action_id": None
    }