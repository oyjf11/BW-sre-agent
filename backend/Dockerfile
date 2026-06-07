FROM python:3.11-slim

# 替换 pip 源为阿里云
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
