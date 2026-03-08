from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List
from app.schemas.message import MessageResponse

class ChatSessionBase(BaseModel):
    title: str = Field(default="New Chat", max_length=100)
    

class ChatSessionCreate(ChatSessionBase):
    user_id: int

class ChatSessionResponse(ChatSessionBase):
    id: int
    user_id: int
    created_at: datetime
    messages: List[MessageResponse] = [] 

    model_config = ConfigDict(from_attributes=True)