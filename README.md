# 🍳 Recipe AI Backend

> **Intelligent Recipe Generator** - Extract ingredients from text or images, generate AI-powered recipes, and chat about cooking with context-aware conversations.

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org/)

---

## 🌟 Overview

Recipe AI Backend is a FastAPI application that uses artificial intelligence to help you with cooking. This application can extract ingredients from text or images, generate personalized recipes, and provide interactive chat for each recipe.

### ✨ Key Features

🔍 **Smart Ingredient Extraction**
- Extract from text with natural language processing
- Upload and analyze images with auto-resize & compression
- Accurate food ingredient detection

🤖 **AI-Powered Recipe Generation**
- Generate recipes based on available ingredients
- In-memory caching for optimal performance
- Multiple recipe suggestions per request

💬 **Contextual Chat System**
- Continuous chat within specific recipe context
- Session persistence with SQLite database
- Stored conversation history

🛡️ **Built-in Protection**
- Rate limiting (5 requests/minute per IP)
- CORS support for frontend integration
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
git clone https://github.com/FchDxCode/recipe_ai.git
cd recipe_ai

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your API keys

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

🎉 **That's it!** Access the application at [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📦 Prerequisites

| Requirement | Version | Description |
|-------------|---------|-------------|
| **Python** | ≥ 3.10 | Main runtime |
| **pip** | Latest | Package manager |
| **Node.js** | ≥ 16 | For SDK generation (optional) |
| **Java** | ≥ 8 | For OpenAPI Generator (optional) |

### Optional Tools
- **pipenv** or **poetry** for dependency management
- **Docker** for containerization

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

Create a `.env` file in the root directory:

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

> 💡 **Tip**: Copy `.env.example` to `.env` and edit according to your needs.

---

## 💾 Database Setup

Recipe AI uses SQLite database that will be created automatically when the application runs for the first time.

### Database Schema
- **sessions**: Store session data and context
- **messages**: Chat history and interactions
- **recipes**: Cache for generated recipes

### Migrations (Optional)
To setup migrations with Alembic:

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

Extract ingredients from text or images.

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

Select a recipe to start a chat session.

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
  "message": "Recipe successfully selected. You can now ask questions about this recipe!"
}
```

### 💬 Chat About Recipe
**POST** `/recipes/chat`

Chat about the selected recipe.

#### Request
```json
{
  "context_id": "abc123def456",
  "message": "How can I make the pasta more creamy?"
}
```

#### Response
```json
{
  "reply": "To make pasta more creamy, you can add cream or milk to the sauce..."
}
```

### 🏁 End Session
**POST** `/recipes/end`

End the chat session and clear context.

#### Request
```json
{
  "context_id": "abc123def456"
}
```

#### Response
```json
{
  "message": "Session successfully ended and context has been cleared."
}
```

---

## 🔗 Client SDK Generation

Generate client SDKs for various programming languages using OpenAPI specification.

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

Add scripts to `package.json`:

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

We greatly appreciate your contributions! Here's how to contribute:

### Development Setup
1. Fork this repository
2. Create a new branch: `git checkout -b feature/amazing-feature`
3. Install development dependencies: `pip install -r requirements-dev.txt`
4. Make your changes
5. Run tests: `pytest`
6. Commit changes: `git commit -m 'Add amazing feature'`
7. Push to branch: `git push origin feature/amazing-feature`
8. Create a Pull Request

### Code Style
- Follow PEP 8 for Python code
- Use type hints
- Add docstrings for functions and classes
- Write tests for new features

### Reporting Issues
Use GitHub Issues to report bugs or request new features.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **FastAPI** - Modern web framework for Python
- **OpenRouter** - AI API gateway
- **SQLite** - Lightweight database engine
- **OpenAPI Generator** - Code generation tools

---

<div align="center">

**Made with ❤️ for cooking enthusiasts**

[⭐ Star this repo](https://github.com/FchDxCode/recipe_ai) • [🐛 Report Bug](https://github.com/FchDxCode/recipe_ai/issues) • [💡 Request Feature](https://github.com/FchDxCode/recipe_ai/issues)

</div>