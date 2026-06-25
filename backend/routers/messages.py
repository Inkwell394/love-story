import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import APIRouter, Depends, HTTPException
from backend.database import get_conn
from backend.models import MessageCreate, MessageOut, MessageOutSimple
from backend.auth import get_current_user, optional_user

router = APIRouter(prefix="/api/messages", tags=["留言"])

@router.get("", response_model=list[MessageOut])
def get_messages(_=Depends(optional_user)):
    conn = get_conn()
    rows = conn.execute(
        "SELECT id, text, username, nickname, created_at FROM messages ORDER BY created_at DESC"
    ).fetchall()
    result = []
    for row in rows:
        comments = conn.execute(
            "SELECT id, message_id, text, username, nickname, created_at FROM comments WHERE message_id = ? ORDER BY created_at ASC",
            (row["id"],)
        ).fetchall()
        result.append({
            "id": row["id"],
            "text": row["text"],
            "username": row["username"],
            "nickname": row["nickname"],
            "created_at": row["created_at"],
            "comments": [dict(c) for c in comments]
        })
    conn.close()
    return result

@router.post("", response_model=MessageOutSimple)
def create_message(body: MessageCreate, username: str = Depends(get_current_user)):
    if not body.text.strip():
        raise HTTPException(status_code=400, detail="留言不能为空")
    conn = get_conn()
    nickname = conn.execute("SELECT nickname FROM users WHERE username=?", (username,)).fetchone()
    nick = nickname["nickname"] if nickname else username
    cur = conn.execute(
        "INSERT INTO messages (text, username, nickname) VALUES (?, ?, ?)",
        (body.text.strip(), username, nick)
    )
    conn.commit()
    row = conn.execute("SELECT * FROM messages WHERE id=?", (cur.lastrowid,)).fetchone()
    conn.close()
    return dict(row)

@router.delete("/{message_id}")
def delete_message(message_id: int, username: str = Depends(get_current_user)):
    conn = get_conn()
    row = conn.execute("SELECT * FROM messages WHERE id=?", (message_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="留言不存在")
    if row["username"] != username:
        conn.close()
        raise HTTPException(status_code=403, detail="只能删除自己的留言")
    conn.execute("DELETE FROM messages WHERE id=?", (message_id,))
    conn.commit()
    conn.close()
    return {"ok": True}
