from pydantic import BaseModel, ConfigDict

class ChatRequest(BaseModel):
    session_id: int
    message: str

class ChatResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    content: str
    requires_confirmation: bool = False
    action_id: str | None = None

class ExecuteRequest(BaseModel):
    action_id: str
    confirmed: bool

class ExecuteResponse(BaseModel):
    content: str