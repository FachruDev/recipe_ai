# Stage 1: Install dependencies
FROM python:3.11-slim AS builder
WORKDIR /app

# Install system libs needed by Pillow
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libjpeg-dev zlib1g-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy & install Python deps ke prefix /install
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Copy app code + deps
FROM python:3.11-slim
WORKDIR /app

# Install runtime libs for Pillow
RUN apt-get update && \
    apt-get install -y --no-install-recommends libjpeg-dev && \
    rm -rf /var/lib/apt/lists/*

# copy pip install (packages + entrypoints) to /usr/local
COPY --from=builder /install /usr/local

# Copy code application
COPY . .

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

# Run via Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
