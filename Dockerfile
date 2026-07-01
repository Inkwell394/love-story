FROM python:3.9-slim

WORKDIR /app

# 安装依赖
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目文件
COPY backend/ ./backend/
COPY index.html chat.html login.html register.html forgot-password.html reset-password.html ./
COPY static/ ./static/

# 暴露端口
EXPOSE 8080

# 启动命令
CMD ["sh", "-c", "cd /app && uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
