FROM python:3.12-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 启动服务（禁用演示模式以使用真实 API，如需演示数据保持默认）
ENV DEMO_MODE=1
ENV PORT=8000

EXPOSE 8000

CMD ["python", "server_http.py"]
