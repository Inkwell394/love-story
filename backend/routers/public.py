from fastapi import APIRouter, HTTPException
from database import get_conn
from models import PublicMessageCreate, PublicMessageOut

router = APIRouter(prefix="/api/public", tags=["公开留言"])

@router.get("/messages", response_model=list[PublicMessageOut])
def get_public_messages():
    conn = get_conn()
    rows = conn.execute(
        "SELECT id, nickname, text, created_at FROM public_messages ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

@router.post("/messages", response_model=PublicMessageOut)
def create_public_message(body: PublicMessageCreate):
    nickname = body.nickname.strip()
    text = body.text.strip()
    if not nickname:
        raise HTTPException(status_code=400, detail="请填写你的名字")
    if not text:
        raise HTTPException(status_code=400, detail="内容不能为空")
    if len(nickname) > 20:
        raise HTTPException(status_code=400, detail="名字不能超过20字")
    if len(text) > 500:
        raise HTTPException(status_code=400, detail="内容不能超过500字")
    conn = get_conn()
    cur = conn.execute(
        "INSERT INTO public_messages (nickname, text) VALUES (?, ?)",
        (nickname, text)
    )
    conn.commit()
    row = conn.execute("SELECT * FROM public_messages WHERE id=?", (cur.lastrowid,)).fetchone()
    conn.close()
    return dict(row)