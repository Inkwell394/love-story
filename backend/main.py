import os, sys
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import init_db, get_conn
from auth import hash_password
from routers import auth, messages, comments, blessings

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

uploads_dir = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

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
