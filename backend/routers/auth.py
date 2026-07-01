from fastapi import APIRouter, Depends, HTTPException
from database import get_conn
from models import UserLogin, TokenOut, UserOut
from auth import hash_password, verify_password, create_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["认证"])

@router.post("/login", response_model=TokenOut)
def login(body: UserLogin):
    print(f"[AUTH] Login attempt: {body.username}")
    conn = get_conn()
    user = conn.execute("SELECT * FROM users WHERE username=?", (body.username,)).fetchone()
    conn.close()
    if not user or not verify_password(body.password, user["password_hash"]):
        print(f"[AUTH] Login FAILED for: {body.username}")
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    print(f"[AUTH] Login SUCCESS for: {body.username}")
    token = create_token(user["username"])
    return TokenOut(
        access_token=token,
        user=UserOut(username=user["username"], nickname=user["nickname"])
    )

# ============================================================
# 新增：注册端点，与 Supabase 注册配合使用
# ============================================================
from pydantic import BaseModel

class UserRegister(BaseModel):
    username: str
    password: str
    nickname: str = ""

@router.post("/register", response_model=TokenOut)
def register(body: UserRegister):
    print(f"[AUTH] Register attempt: {body.username}")
    if not body.username or len(body.username) < 2:
        raise HTTPException(status_code=400, detail="用户名至少2个字符")
    if not body.password or len(body.password) < 6:
        raise HTTPException(status_code=400, detail="密码至少6位")

    conn = get_conn()
    existing = conn.execute("SELECT username FROM users WHERE username=?", (body.username,)).fetchone()
    if existing:
        conn.close()
        raise HTTPException(status_code=409, detail="用户名已被注册")

    nickname = body.nickname.strip() or body.username
    conn.execute(
        "INSERT INTO users (username, password_hash, nickname) VALUES (?, ?, ?)",
        (body.username, hash_password(body.password), nickname)
    )
    conn.commit()
    conn.close()

    print(f"[AUTH] Register SUCCESS for: {body.username}")
    token = create_token(body.username)
    return TokenOut(
        access_token=token,
        user=UserOut(username=body.username, nickname=nickname)
    )

@router.get("/me", response_model=UserOut)
def get_me(username: str = Depends(get_current_user)):
    conn = get_conn()
    user = conn.execute("SELECT username, nickname FROM users WHERE username=?", (username,)).fetchone()
    conn.close()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return dict(user)

# ============================================================
# 新增：Supabase session 同步端点
# 前端在 Supabase 登录成功后调用此端点创建/获取本地用户
# ============================================================
class SupabaseSyncBody(BaseModel):
    email: str
    nickname: str = ""
    supabase_id: str = ""

@router.post("/supabase-sync")
def sync_supabase_user(body: SupabaseSyncBody):
    """用 Supabase 用户信息同步到本地用户表"""
    if not body.email:
        raise HTTPException(status_code=400, detail="邮箱不能为空")
    username = body.email.split("@")[0]
    nickname = body.nickname.strip() or username
    conn = get_conn()
    existing = conn.execute("SELECT username, nickname FROM users WHERE username=?", (username,)).fetchone()
    if existing:
        conn.close()
        token = create_token(existing["username"])
        return TokenOut(
            access_token=token,
            user=UserOut(username=existing["username"], nickname=existing["nickname"])
        )
    # 新用户，用随机密码创建（不能直接密码登录）
    import secrets
    random_pwd = secrets.token_hex(16)
    conn.execute(
        "INSERT INTO users (username, password_hash, nickname) VALUES (?, ?, ?)",
        (username, hash_password(random_pwd), nickname)
    )
    conn.commit()
    conn.close()
    token = create_token(username)
    return TokenOut(
        access_token=token,
        user=UserOut(username=username, nickname=nickname)
    )
