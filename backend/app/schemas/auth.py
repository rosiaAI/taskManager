from datetime import datetime

from pydantic import BaseModel, ConfigDict

class Token(BaseModel):
    access_token: str
    token_type: str

class UserBase(BaseModel):
    email: str
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)