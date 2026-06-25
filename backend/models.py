from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# ===== 用户 =====
class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    username: str
    nickname: str

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

# ===== 留言 =====
class MessageCreate(BaseModel):
    text: str

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
    text: str

class CommentOut(BaseModel):
    id: int
    message_id: int
    text: str
    username: str
    nickname: str
    created_at: str
