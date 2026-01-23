FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy requirements trước (tối ưu cache)
COPY System/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY System/ .

EXPOSE 5000

CMD ["python", "app.py"]

