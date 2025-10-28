FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .


RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

# Set environment variables
# ENV PYTHONPATH=/app
# ENV HOST=0.0.0.0
# ENV PORT=8080

# ENV GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json


# VOLUME ["/app/credentials.json"]


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]