from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class ChatRequest(BaseModel):
    session_id: int
    message: str

class ChatResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    assistant_reply: str