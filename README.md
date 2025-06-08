# 🍳 Recipe AI Backend

> **Intelligent Recipe Generator** - Extract ingredients from text or images, generate AI-powered recipes, and chat about cooking with context-aware conversations.

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org/)

---

## 🌟 Overview

Recipe AI Backend adalah aplikasi FastAPI yang menggunakan kecerdasan buatan untuk membantu Anda dalam memasak. Aplikasi ini dapat mengekstrak bahan-bahan dari teks atau gambar, menghasilkan resep yang dipersonalisasi, dan menyediakan chat interaktif untuk setiap resep.

### ✨ Key Features

🔍 **Smart Ingredient Extraction**
- Extract dari teks dengan pemrosesan natural language
- Upload dan analisis gambar dengan auto-resize & compression
- Deteksi bahan makanan yang akurat

🤖 **AI-Powered Recipe Generation**
- Generate resep berdasarkan bahan yang tersedia
- Caching in-memory untuk performa optimal
- Multiple recipe suggestions per request

💬 **Contextual Chat System**
- Chat berkelanjutan dalam konteks resep tertentu
- Session persistence dengan SQLite database
- Riwayat percakapan yang tersimpan

🛡️ **Built-in Protection**
- Rate limiting (5 requests/minute per IP)
- CORS support untuk frontend integration
- Comprehensive error handling

📚 **Developer Friendly**
- Auto-generated OpenAPI documentation
- Client SDK generator support
- Docker ready configuration

---

## 📋 Table of Contents

- [🚀 Quick Start](#-quick-start)
- [📦 Prerequisites](#-prerequisites)
- [🔧 Installation](#-installation)
- [⚙️ Configuration](#️-configuration)
- [💾 Database Setup](#-database-setup)
- [▶️ Running the Application](#️-running-the-application)
- [📖 API Documentation](#-api-documentation)
- [🔗 Client SDK Generation](#-client-sdk-generation)
- [🐳 Docker Deployment](#-docker-deployment)
- [🤝 Contributing](#-contributing)

---

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/username/recipe_ai.git
cd recipe_ai

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env dengan API keys Anda

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

🎉 **That's it!** Akses aplikasi di [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📦 Prerequisites

| Requirement | Version | Description |
|-------------|---------|-------------|
| **Python** | ≥ 3.10 | Main runtime |
| **pip** | Latest | Package manager |
| **Node.js** | ≥ 16 | For SDK generation (optional) |
| **Java** | ≥ 8 | For OpenAPI Generator (optional) |

### Optional Tools
- **pipenv** atau **poetry** untuk dependency management
- **Docker** untuk containerization

---

## 🔧 Installation

### Method 1: Standard Installation
```bash
# Clone the repository
git clone https://github.com/username/recipe_ai.git
cd recipe_ai

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Method 2: Using pipenv
```bash
git clone https://github.com/username/recipe_ai.git
cd recipe_ai
pipenv install
pipenv shell
```

---

## ⚙️ Configuration

### Environment Variables

Buat file `.env` di root directory:

```dotenv
# ===========================================
# RECIPE AI CONFIGURATION
# ===========================================

# OpenRouter API Configuration
OPENROUTER_API_KEY=sk-your-openrouter-api-key-here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Database Configuration
DATABASE_FILE=recipe_ai.db

# Application Settings (Optional)
DEBUG=true
LOG_LEVEL=info
MAX_IMAGE_SIZE=5242880  # 5MB in bytes
RATE_LIMIT_REQUESTS=5
RATE_LIMIT_WINDOW=60    # seconds
```

### Configuration Options

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENROUTER_API_KEY` | ✅ | - | Your OpenRouter API key |
| `OPENROUTER_BASE_URL` | ❌ | `https://openrouter.ai/api/v1` | OpenRouter base URL |
| `DATABASE_FILE` | ❌ | `recipe_ai.db` | SQLite database filename |
| `DEBUG` | ❌ | `false` | Enable debug mode |
| `LOG_LEVEL` | ❌ | `info` | Logging level |

> 💡 **Tip**: Copy `.env.example` ke `.env` dan edit sesuai kebutuhan Anda.

---

## 💾 Database Setup

Recipe AI menggunakan SQLite database yang akan dibuat otomatis saat aplikasi pertama kali dijalankan.

### Database Schema
- **sessions**: Menyimpan session data dan context
- **messages**: Riwayat chat dan interaksi
- **recipes**: Cache resep yang di-generate

### Migrations (Optional)
Untuk setup migrations dengan Alembic:

```bash
pip install alembic
alembic init alembic
# Setup your migration files
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

---

## ▶️ Running the Application

### Development Mode
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Access Points
| Service | URL | Description |
|---------|-----|-------------|
| **Swagger UI** | [http://localhost:8000/docs](http://localhost:8000/docs) | Interactive API documentation |
| **ReDoc** | [http://localhost:8000/redoc](http://localhost:8000/redoc) | Alternative API documentation |
| **OpenAPI Spec** | [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json) | Raw OpenAPI specification |

---

## 📖 API Documentation

### Base URL
```
http://localhost:8000/api
```

### 🔍 Extract Ingredients
**POST** `/ingredients`

Extract ingredients dari teks atau gambar.

#### Request (Multipart Form)
```bash
# Text extraction
curl -X POST "http://localhost:8000/api/ingredients" \
  -F "text=I have tomatoes, onions, and garlic"

# Image extraction
curl -X POST "http://localhost:8000/api/ingredients" \
  -F "image=@path/to/image.jpg"
```

#### Response
```json
{
  "context_id": "abc123def456",
  "recipes": [
    {
      "id": "recipe_001",
      "title": "Tomato Garlic Pasta",
      "description": "Simple and delicious pasta dish",
      "ingredients": ["tomatoes", "onions", "garlic", "pasta"],
      "instructions": ["Step 1...", "Step 2..."],
      "prep_time": 15,
      "cook_time": 20
    }
  ]
}
```

### 🎯 Select Recipe
**POST** `/recipes/select`

Pilih resep untuk memulai chat session.

#### Request
```json
{
  "context_id": "abc123def456",
  "recipe_id": "recipe_001"
}
```

#### Response
```json
{
  "message": "Resep berhasil dipilih. Anda dapat mulai bertanya tentang resep ini!"
}
```

### 💬 Chat About Recipe
**POST** `/recipes/chat`

Chat tentang resep yang dipilih.

#### Request
```json
{
  "context_id": "abc123def456",
  "message": "Bagaimana cara membuat pasta lebih creamy?"
}
```

#### Response
```json
{
  "reply": "Untuk membuat pasta lebih creamy, Anda bisa menambahkan cream atau susu ke dalam saus..."
}
```

### 🏁 End Session
**POST** `/recipes/end`

Akhiri chat session dan hapus context.

#### Request
```json
{
  "context_id": "abc123def456"
}
```

#### Response
```json
{
  "message": "Session berhasil diakhiri dan context telah dihapus."
}
```

---

## 🔗 Client SDK Generation

Generate client SDK untuk berbagai bahasa pemrograman menggunakan OpenAPI specification.

### 1. Install OpenAPI Generator

#### Using npm (Recommended)
```bash
npm install @openapitools/openapi-generator-cli -g
```

#### Using Docker
```bash
docker pull openapitools/openapi-generator-cli
```

### 2. Generate SDK

#### TypeScript/JavaScript
```bash
openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g typescript-fetch \
  -o ./client-sdk/typescript-fetch \
  --additional-properties=typescriptThreePlus=true
```

#### Python Client
```bash
openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g python \
  -o ./client-sdk/python \
  --additional-properties=packageName=recipe_ai_client
```

#### Other Languages
```bash
# Java
openapi-generator-cli generate -i http://localhost:8000/openapi.json -g java -o ./client-sdk/java

# PHP
openapi-generator-cli generate -i http://localhost:8000/openapi.json -g php -o ./client-sdk/php

# Go
openapi-generator-cli generate -i http://localhost:8000/openapi.json -g go -o ./client-sdk/go
```

### 3. Automated SDK Generation

Tambahkan script di `package.json`:

```json
{
  "scripts": {
    "gen-sdk": "openapi-generator-cli generate -i http://localhost:8000/openapi.json -g typescript-fetch -o ./src/lib/sdk",
    "gen-sdk:python": "openapi-generator-cli generate -i http://localhost:8000/openapi.json -g python -o ./client-sdk/python"
  }
}
```

---

## 🐳 Docker Deployment

### Development with Docker

#### Dockerfile
```dockerfile
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### docker-compose.yml
```yaml
version: '3.8'

services:
  recipe-ai:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
      - ./data:/app/data
    environment:
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - DATABASE_FILE=data/recipe_ai.db
    restart: unless-stopped

  # Optional: Add nginx reverse proxy
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - recipe-ai
    restart: unless-stopped
```

### Quick Docker Commands
```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f recipe-ai

# Stop services
docker-compose down
```

---

## 🤝 Contributing

Kami sangat menghargai kontribusi Anda! Berikut cara untuk berkontribusi:

### Development Setup
1. Fork repository ini
2. Buat branch baru: `git checkout -b feature/amazing-feature`
3. Install development dependencies: `pip install -r requirements-dev.txt`
4. Buat perubahan Anda
5. Jalankan tests: `pytest`
6. Commit perubahan: `git commit -m 'Add amazing feature'`
7. Push ke branch: `git push origin feature/amazing-feature`
8. Buat Pull Request

### Code Style
- Follow PEP 8 untuk Python code
- Gunakan type hints
- Tambahkan docstrings untuk functions dan classes
- Write tests untuk features baru

### Reporting Issues
Gunakan GitHub Issues untuk melaporkan bug atau request fitur baru.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **FastAPI** - Modern web framework untuk Python
- **OpenRouter** - AI API gateway
- **SQLite** - Lightweight database engine
- **OpenAPI Generator** - Code generation tools

---

<div align="center">

**Made with ❤️ for cooking enthusiasts**

[⭐ Star this repo](https://github.com/username/recipe_ai) • [🐛 Report Bug](https://github.com/username/recipe_ai/issues) • [💡 Request Feature](https://github.com/username/recipe_ai/issues)

</div>