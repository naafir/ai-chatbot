"""
Pydantic Schemas (Request/Response Models)
These define the shape of API request bodies and response data.
FastAPI uses these for automatic validation and documentation.
"""

from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime


# â”€â”€â”€ Auth Schemas â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class SignupRequest(BaseModel):
    """Schema for POST /api/auth/signup"""
    username: str
    email: EmailStr
    password: str

    @validator("username")
    def username_valid(cls, v):
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        if len(v) > 50:
            raise ValueError("Username must be under 50 characters")
        if not v.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Username can only contain letters, numbers, - and _")
        return v

    @validator("password")
    def password_valid(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class LoginRequest(BaseModel):
    """Schema for POST /api/auth/login"""
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    """Response returned after successful login or signup"""
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    email: str


class UserResponse(BaseModel):
    """Public user profile data"""
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


# â”€â”€â”€ Chat Schemas â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

class SendMessageRequest(BaseModel):
    """Schema for POST /api/chat/message"""
    chat_id: Optional[int] = None   # None = create new chat
    message: str

    @validator("message")
    def message_not_empty(cls, v):
        v = v.strip()
        if not v:
            raise ValueError("Message cannot be empty")
        if len(v) > 10000:
            raise ValueError("Message too long (max 10,000 characters)")
        return v


class MessageResponse(BaseModel):
    """A single message in a chat"""
    id: int
    chat_id: int
    role: str
    content: str
    timestamp: datetime

    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    """A chat session summary"""
    id: int
    user_id: int
    title: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatWithMessagesResponse(BaseModel):
    """A chat session with all its messages"""
    id: int
    user_id: int
    title: str
    created_at: datetime
    messages: List[MessageResponse]

    class Config:
        from_attributes = True


class SendMessageResponse(BaseModel):
    """Response after sending a message"""
    chat_id: int
    user_message: MessageResponse
    ai_message: MessageResponse
    chat_title: str


class DeleteChatResponse(BaseModel):
    """Response after deleting a chat"""
    success: bool
    message: str


