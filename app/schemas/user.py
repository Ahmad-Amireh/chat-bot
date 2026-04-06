from pydantic import BaseModel, EmailStr, ConfigDict, Field

from pydantic import BaseModel, Field, EmailStr
from pydantic import ConfigDict

class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=20)
    email: EmailStr = Field(..., max_length=120)

class UserCreate(UserBase): 
    password:str = Field(..., min_length=6, max_length=128)

class UserPublicResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name:str

class UserPrivateResponse(UserPublicResponse):
    model_config = ConfigDict(from_attributes=True)
    email: EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str

class LoginRequest(BaseModel):
    email: str
    password: str