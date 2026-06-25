import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi import APIRouter, Depends, HTTPException
from backend.database import get_conn
from backend.models import CommentCreate, CommentOut
from backend.auth import get_current_user

router = APIRouter(prefix="/api/comments", tags=["评论"])

@router.post("/{message_id}", response_model=CommentOut)
def create_comment(message_id: int, body: CommentCreate, username: str = Depends(get_current_user)):
    if not body.text.strip():
        raise HTTPException(status_code=400, detail="评论不能为空")
    conn = get_conn()
    msg = conn.execute("SELECT id FROM messages WHERE id=?", (message_id,)).fetchone()
    if not msg:
        conn.close()
        raise HTTPException(status_code=404, detail="留言不存在")
    nickname = conn.execute("SELECT nickname FROM users WHERE username=?", (username,)).fetchone()
    nick = nickname["nickname"] if nickname else username
    cur = conn.execute(
        "INSERT INTO comments (message_id, text, username, nickname) VALUES (?, ?, ?, ?)",
        (message_id, body.text.strip(), username, nick)
    )
    conn.commit()
    row = conn.execute("SELECT * FROM comments WHERE id=?", (cur.lastrowid,)).fetchone()
    conn.close()
    return dict(row)

@router.delete("/{message_id}/{comment_id}")
def delete_comment(message_id: int, comment_id: int, username: str = Depends(get_current_user)):
    conn = get_conn()
    row = conn.execute("SELECT * FROM comments WHERE id=? AND message_id=?", (comment_id, message_id)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="评论不存在")
    if row["username"] != username:
        conn.close()
        raise HTTPException(status_code=403, detail="只能删除自己的评论")
    conn.execute("DELETE FROM comments WHERE id=?", (comment_id,))
    conn.commit()
    conn.close()
    return {"ok": True}
