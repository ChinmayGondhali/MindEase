from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


# ── AUTH ──────────────────────────────────────
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    display_name: Optional[str] = "Anonymous"

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    uid: str
    email: str
    display_name: str
    created_at: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ── CHAT ──────────────────────────────────────
class MessageRole(str, Enum):
    user = "user"
    bot  = "bot"


class ChatMessage(BaseModel):
    content: str
    role: MessageRole = MessageRole.user


class ChatMessageResponse(BaseModel):
    id: Optional[str] = None
    user_id: str
    content: str
    role: str
    sentiment_score: Optional[float] = None
    sentiment_level: Optional[str] = None
    timestamp: Optional[str] = None


class ChatSessionResponse(BaseModel):
    session_id: str
    messages: List[ChatMessageResponse]
    created_at: Optional[str] = None


class BotReply(BaseModel):
    message: str
    sentiment_score: float
    sentiment_level: str
    crisis_detected: bool
    helplines: Optional[List[dict]] = None


# ── CRISIS ────────────────────────────────────
class CrisisLevel(str, Enum):
    low      = "low"
    medium   = "medium"
    high     = "high"
    critical = "critical"


class CrisisLog(BaseModel):
    user_id: str
    message: str
    sentiment_score: float
    crisis_level: CrisisLevel
    timestamp: Optional[str] = None


class CrisisLogResponse(BaseModel):
    id: str
    user_id: str
    message: str
    sentiment_score: float
    crisis_level: str
    timestamp: str
    resolved: bool = False


# ── MOOD ──────────────────────────────────────
class MoodEntry(BaseModel):
    mood: str
    score: int
    note: Optional[str] = ""
