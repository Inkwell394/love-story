from fastapi import APIRouter, HTTPException
from database import get_conn
from models import BlessingCreate, BlessingOut

router = APIRouter(prefix="/api/blessings", tags=["祝福"])

@router.get("", response_model=list[BlessingOut])
def get_blessings():
    """获取所有祝福（无需登录）"""
    conn = get_conn()
    rows = conn.execute(
        "SELECT id, name, text, created_at FROM blessings ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

@router.post("", response_model=BlessingOut)
def create_blessing(body: BlessingCreate):
    """发表祝福（无需登录）"""
    name = body.name.strip()
    text = body.text.strip()
    if not name:
        raise HTTPException(status_code=400, detail="请填写你的名字")
    if not text:
        raise HTTPException(status_code=400, detail="祝福不能为空")
    if len(name) > 30:
        raise HTTPException(status_code=400, detail="名字不能超过30字")
    if len(text) > 300:
        raise HTTPException(status_code=400, detail="祝福不能超过300字")
    conn = get_conn()
    cur = conn.execute(
        "INSERT INTO blessings (name, text) VALUES (?, ?)",
        (name, text)
    )
    conn.commit()
    row = conn.execute("SELECT * FROM blessings WHERE id=?", (cur.lastrowid,)).fetchone()
    conn.close()
    return dict(row)
