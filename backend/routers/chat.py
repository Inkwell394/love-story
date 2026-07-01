from fastapi import APIRouter, Depends, HTTPException
from database import get_conn
from models import ChatMessageCreate, ChatMessageOut
from auth import get_current_user

router = APIRouter(prefix="/api/chat", tags=["情侣私聊"])

@router.get("/messages", response_model=list[ChatMessageOut])
def get_chat_messages(username: str = Depends(get_current_user)):
    print(f"[CHAT] GET messages by user: {username}")
    conn = get_conn()
    rows = conn.execute(
        "SELECT id, sender, text, created_at FROM couple_chat ORDER BY created_at ASC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

@router.post("/messages", response_model=ChatMessageOut)
def send_chat_message(body: ChatMessageCreate, sender: str = Depends(get_current_user)):
    print(f"[CHAT] POST by {sender}: {body.text[:50]}")
    text = body.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="消息不能为空")
    if len(text) > 1000:
        raise HTTPException(status_code=400, detail="消息不能超过1000字")
    conn = get_conn()
    cur = conn.execute(
        "INSERT INTO couple_chat (sender, text) VALUES (?, ?)",
        (sender, text)
    )
    conn.commit()
    row = conn.execute("SELECT * FROM couple_chat WHERE id=?", (cur.lastrowid,)).fetchone()
    conn.close()
    return dict(row)

@router.delete("/messages/{message_id}")
def delete_chat_message(message_id: int, username: str = Depends(get_current_user)):
    conn = get_conn()
    row = conn.execute("SELECT * FROM couple_chat WHERE id=?", (message_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="消息不存在")
    if row["sender"] != username:
        conn.close()
        raise HTTPException(status_code=403, detail="只能删除自己的消息")
    conn.execute("DELETE FROM couple_chat WHERE id=?", (message_id,))
    conn.commit()
    conn.close()
    return {"ok": True}