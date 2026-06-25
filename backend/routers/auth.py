import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import APIRouter, Depends, HTTPException
from backend.database import get_conn
from backend.models import UserLogin, TokenOut, UserOut
from backend.auth import hash_password, verify_password, create_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["认证"])

@router.post("/login", response_model=TokenOut)
def login(body: UserLogin):
    conn = get_conn()
    user = conn.execute("SELECT * FROM users WHERE username=?", (body.username,)).fetchone()
    conn.close()
    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    token = create_token(user["username"])
    return TokenOut(
        access_token=token,
        user=UserOut(username=user["username"], nickname=user["nickname"])
    )

@router.get("/me", response_model=UserOut)
def get_me(username: str = Depends(get_current_user)):
    conn = get_conn()
    user = conn.execute("SELECT username, nickname FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return dict(user)
