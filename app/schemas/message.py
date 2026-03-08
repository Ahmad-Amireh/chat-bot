from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class MessageBase(BaseModel):
    role: str = Field(..., max_length=20)  # "user", "assistant", "system"
    content: str = Field(...)
    session_id: int

class MessageCreate(MessageBase):
    pass

class MessageResponse(MessageBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)