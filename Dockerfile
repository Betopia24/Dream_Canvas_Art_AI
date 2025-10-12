FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install build dependencies required for some Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies (including google-cloud-storage from requirements.txt)
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .
# Expose port
EXPOSE 8080

# Set environment variables
ENV PYTHONPATH=/app
ENV HOST=0.0.0.0
ENV PORT=8080
# Recommended runtime path for mounted service account credentials
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json

# Do NOT bake credentials into the image - mount them at runtime.
# Provide a mount point for credentials (users should mount their credentials.json here)
VOLUME ["/app/credentials.json"]

# Start the application directly. The container expects credentials.json to be mounted
# at /app/credentials.json (or GOOGLE_APPLICATION_CREDENTIALS env to point elsewhere).
CMD ["python", "main.py"]