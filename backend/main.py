import os, sys
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import init_db, get_conn
from auth import hash_password
from routers import auth, messages, comments, blessings, public, chat

app = FastAPI(title="Love Story API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(messages.router)
app.include_router(comments.router)
app.include_router(blessings.router)
app.include_router(public.router)
app.include_router(chat.router)

from fastapi.responses import FileResponse, HTMLResponse

@app.get("/")
def serve_index():
    return HTMLResponse(open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "index.html"), encoding="utf-8").read())

@app.get("/chat")
def serve_chat():
    return HTMLResponse(open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "chat.html"), encoding="utf-8").read())

# ============================================================
# 新增：Supabase 认证页面路由
# ============================================================
@app.get("/login")
def serve_login():
    return HTMLResponse(open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "login.html"), encoding="utf-8").read())

@app.get("/register")
def serve_register():
    return HTMLResponse(open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "register.html"), encoding="utf-8").read())

@app.get("/forgot-password")
def serve_forgot_password():
    return HTMLResponse(open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "forgot-password.html"), encoding="utf-8").read())

@app.get("/reset-password")
def serve_reset_password():
    return HTMLResponse(open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "reset-password.html"), encoding="utf-8").read())


@app.get("/img/{filename:path}")
def serve_img(filename: str):
    if not filename:
        from fastapi.responses import JSONResponse
        return JSONResponse({"error": "filename required"}, status_code=400)
    return FileResponse(os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "images", filename))

@app.get("/shipin/{filename:path}")
def serve_shipin(filename: str):
    return FileResponse(os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "videos", filename))

uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# ============================================================
# 新增：静态文件目录（Supabase 认证客户端 JS 等）
# ============================================================
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    print(f"Static directory mounted: {static_dir}")
else:
    print(f"Warning: static directory not found at {static_dir}")


@app.on_event("startup")
def startup():
    init_db()
    seed_users()

def seed_users():
    conn = get_conn()
    existing = conn.execute("SELECT COUNT(*) as cnt FROM users").fetchone()
    if existing["cnt"] == 0:
        # ===== 在这里修改你们的账号密码 =====
        users = [
            ("admin", "love123456", "\u6211"),       # 你的账号
            ("girl", "love123456", "\u5979"),        # 女朋友的账号
        ]
        for username, password, nickname in users:
            conn.execute(
                "INSERT INTO users (username, password_hash, nickname) VALUES (?, ?, ?)",
                (username, hash_password(password), nickname)
            )
        conn.commit()
        print("Default users created!")
    conn.close()

@app.get("/api/health")
def health():
    return {"status": "ok", "message": "Love Story API is running"}




