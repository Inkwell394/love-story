from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

import os
import json
import base64
import hashlib
import hmac
import requests

# ============================================================
# 修改：添加 Supabase JWT 验证支持，同时保留原有 JWT 系统
# 原有 JWT + Supabase JWT 双验证模式
# ============================================================

# ---------- 原有配置 ----------
SECRET_KEY = os.getenv("LOVE_SECRET_KEY", "love-story-secret-key-change-in-production-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 30

# ---------- 新增：Supabase 配置 ----------
# 从环境变量读取 Supabase 配置
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "")
# Supabase anon key 的一半（用于验证 anon key 签名的 token）
# 如果未配置 SUPABASE_JWT_SECRET，则尝试从 URL 获取 JWKS
SUPABASE_JWKS_CACHE = None
SUPABASE_JWKS_CACHE_TIME = None

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
auth_scheme = HTTPBearer(auto_error=False)

def hash_password(password: str) -> str:
    return pwd_ctx.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_ctx.verify(plain, hashed)

# ---------- 原有 Token 创建/验证 ----------
def create_token(username: str) -> str:
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    return jwt.encode({"sub": username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None

# ---------- 新增：Supabase JWT 验证 ----------
def get_supabase_jwks():
    """获取 Supabase JWKS 密钥集"""
    global SUPABASE_JWKS_CACHE, SUPABASE_JWKS_CACHE_TIME
    import time
    now = time.time()
    # 缓存 1 小时
    if SUPABASE_JWKS_CACHE and SUPABASE_JWKS_CACHE_TIME and (now - SUPABASE_JWKS_CACHE_TIME) < 3600:
        return SUPABASE_JWKS_CACHE
    if not SUPABASE_URL:
        return None
    try:
        # 从 Supabase 项目获取 JWKS
        jwks_url = f"{SUPABASE_URL}/.well-known/jwks.json"
        resp = requests.get(jwks_url, timeout=5)
        if resp.status_code == 200:
            SUPABASE_JWKS_CACHE = resp.json()
            SUPABASE_JWKS_CACHE_TIME = now
            return SUPABASE_JWKS_CACHE
    except Exception as e:
        print(f"[Supabase] 获取 JWKS 失败: {e}")
    return None

def decode_supabase_token(token: str) -> dict:
    """验证 Supabase JWT 并返回用户信息"""
    if not token:
        return None
    try:
        # 尝试用 HS256（JWT secret）验证
        if SUPABASE_JWT_SECRET:
            payload = jwt.decode(
                token,
                SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                options={"verify_aud": False}
            )
            return payload
    except JWTError:
        pass

    # 尝试用 JWKS (RS256) 验证
    try:
        jwks = get_supabase_jwks()
        if jwks:
            # 从 JWKS 获取公钥
            from jose import jwk as jose_jwk
            for key_data in jwks.get("keys", []):
                try:
                    public_key = jose_jwk.construct(key_data)
                    payload = jwt.decode(
                        token,
                        public_key,
                        algorithms=["RS256"],
                        options={"verify_aud": False}
                    )
                    return payload
                except Exception:
                    continue
    except Exception as e:
        print(f"[Supabase] JWKS 验证失败: {e}")

    return None

def get_supabase_user_from_token(token: str) -> dict:
    """从 Supabase JWT 中提取用户信息"""
    payload = decode_supabase_token(token)
    if not payload:
        return None
    user_id = payload.get("sub")
    email = payload.get("email", "")
    user_metadata = payload.get("user_metadata", {})
    nickname = user_metadata.get("nickname", email.split("@")[0] if email else "用户")
    return {
        "username": email.split("@")[0] if email else user_id,
        "email": email,
        "nickname": nickname,
        "sub": user_id
    }

# ---------- 修改：双验证 get_current_user ----------
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    """同时支持原有 JWT 和 Supabase JWT 的验证"""
    if credentials is None:
        print("[AUTH] No credentials provided")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="请先登录")

    token = credentials.credentials
    token_preview = token[:20] + "..."

    # 1. 尝试原有 JWT 验证
    username = decode_token(token)
    if username:
        print(f"[AUTH] 原有 JWT OK for user: {username}")
        return username

    # 2. 尝试 Supabase JWT 验证
    sb_user = get_supabase_user_from_token(token)
    if sb_user:
        # 将 Supabase 用户映射为用户名
        username = sb_user["username"]
        print(f"[AUTH] Supabase JWT OK for user: {sb_user.get('email', username)}")
        return username

    print(f"[AUTH] Token decode FAILED for: {token_preview}")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="登录已过期，请重新登录"
    )

# ---------- 修改：可选用户验证（兼容未登录）----------
async def optional_user(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    if credentials is None:
        return None
    token = credentials.credentials
    username = decode_token(token)
    if username:
        return username
    sb_user = get_supabase_user_from_token(token)
    if sb_user:
        return sb_user["username"]
    return None

# ---------- 新增：获取完整的用户信息 ----------
async def get_current_user_full(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)):
    """返回完整用户信息（包括来源）"""
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="请先登录")
    token = credentials.credentials

    # 原有 JWT
    username = decode_token(token)
    if username:
        return {"username": username, "auth_source": "legacy"}

    # Supabase JWT
    sb_user = get_supabase_user_from_token(token)
    if sb_user:
        return {"username": sb_user["username"], "auth_source": "supabase", "email": sb_user.get("email")}

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="登录已过期")
