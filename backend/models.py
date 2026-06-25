from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# ===== 用户 =====
class UserLogin(BaseModel):
    username: str
    password: str  # min 6 chars

class UserOut(BaseModel):
    username: str
    nickname: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

# ===== 留言 =====
class MessageCreate(BaseModel):
    text: str  # max 500 chars

class MessageOut(BaseModel):
    id: int
    text: str
    username: str
    nickname: str
    created_at: str
    comments: List["CommentOut"] = []

class MessageOutSimple(BaseModel):
    id: int
    text: str
    username: str
    nickname: str
    created_at: str

# ===== 评论 =====
class CommentCreate(BaseModel):
    text: str  # max 300 chars

class CommentOut(BaseModel):
    id: int
    message_id: int
    text: str
    username: str
    nickname: str
    created_at: str


# ===== ?? =====
class BlessingCreate(BaseModel):
    name: str
    text: str

class BlessingOut(BaseModel):
    id: int
    name: str
    text: str
    created_at: str
