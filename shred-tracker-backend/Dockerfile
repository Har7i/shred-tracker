# 1. 基础镜像：使用轻量级的python 3.10
FROM python:3.10-slim

# 2. 设置环境变量
# 防止Python产生 .pyc 编译文件
ENV PYTHONDONTWRITEBYTECODE 1
# 强制 stdout/stderr 流不经过缓冲直接输出，方便在docker日志中看到实时报错
ENV PYTHONUNBUFFERED 1

# 3. 设置工作目录
WORKDIR /app

# 4. 安装系统依赖 （SQLite 需要一些基础包）
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 5. 安装Python 依赖
# 先拷贝 requirements.txt，利用Docker 的层缓存机制加速镜像构建
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. 拷贝项目代码
COPY . .

# 7. 暴露 FastAPI 默认端口
EXPOSE 8000

# 8. 启动命令：使用uvicorn运行app文件下的main.py中的app实例
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]