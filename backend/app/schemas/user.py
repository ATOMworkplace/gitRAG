# app/schemas/user.py

from pydantic import BaseModel, EmailStr

class UserInfo(BaseModel):
    id: str
    name: str
    email: EmailStr
    picture: str
    provider: str

    class Config:
        from_attributes = True  