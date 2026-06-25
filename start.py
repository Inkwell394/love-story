"""启动脚本 - 解决 Render 上缺少 __init__.py 的问题"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from main import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
