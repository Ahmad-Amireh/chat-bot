from pydantic import BaseModel, EmailStr, ConfigDict, Field

from pydantic import BaseModel, Field, EmailStr
from pydantic import ConfigDict

class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=20)
    email: EmailStr = Field(..., max_length=120)

class UserCreate(UserBase): 
    pass

class UserResponse(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
