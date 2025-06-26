FROM python:3.13-alpine
WORKDIR /app
COPY requirements.txt /app/
RUN apk add --no-cache netcat-openbsd postgresql-client
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

