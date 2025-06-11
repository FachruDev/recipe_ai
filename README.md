# 🍳 Chef AI: Smart Recipe Generator Backend

> Transform your ingredients into delicious recipes with AI-powered cooking assistance

Chef AI is an intelligent, conversational backend service that revolutionizes home cooking by converting user-provided ingredients into personalized recipes. Leveraging cutting-edge multimodal AI technology, it understands ingredients from both text descriptions and images, generates tailored recipe suggestions, and provides interactive cooking guidance through an intelligent chat interface.

## ✨ Key Features

### 🧠 **Multimodal Ingredient Recognition**
- **Text Input**: Simply list your available ingredients as text
- **Image Upload**: Take a photo of your fridge contents or ingredients for automatic recognition
- **Smart Processing**: Advanced AI understands various ingredient formats and presentations

### 🧑‍🍳 **Dynamic Recipe Generation**
- **Multiple Options**: Generates three unique, practical recipes from your ingredients
- **Home-Cooking Focused**: Recipes designed for real home kitchens with realistic preparation times
- **Ingredient Optimization**: Makes the most of what you have while suggesting minimal additions

### 💬 **Context-Aware AI Chat**
- **Interactive Guidance**: Ask questions about cooking techniques, substitutions, or modifications
- **Recipe-Focused**: AI stays strictly on-topic, providing relevant cooking assistance
- **Step-by-Step Help**: Get detailed explanations for any part of the cooking process

### 🛡️ **Robust AI Control**
- **Advanced Prompt Engineering**: Ensures reliable, focused responses
- **Manipulation Resistant**: Protected against off-topic conversation attempts
- **Consistent Behavior**: Reliable AI persona across all interactions

### 🚀 **Performance & Architecture**
- **High Performance**: Built with FastAPI for optimal speed and scalability
- **Clean Architecture**: Modular design with clear separation of concerns
- **Smart Optimization**: Automatic image preprocessing reduces costs and improves response times
- **Rate Protection**: Built-in rate limiting prevents API abuse

## ⚙️ Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend Framework** | FastAPI |
| **AI Integration** | OpenRouter API |
| **Database** | SQLModel with SQLite |
| **Data Validation** | Pydantic |
| **Image Processing** | Pillow (PIL) |
| **Containerization** | Docker & Docker Compose |

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ (for local development)
- Docker & Docker Compose (recommended)
- OpenRouter API key

### 📋 Configuration

1. **Create environment file**:
   ```bash
   cp .env.example .env
   ```

2. **Configure your API key**:
   ```env
   # .env file
   
   # Your OpenRouter API key (required)
   OPENROUTER_API_KEY="sk-or-v1-your-key-here"
   
   # OpenRouter API base URL (default: no change needed)
   OPENROUTER_BASE_URL="https://openrouter.ai/api/v1"
   
   # Database configuration
   DATABASE_FILE="chef_ai.db"
   ```

### 🐳 Option 1: Docker (Recommended)

**Why Docker?** Handles all dependencies automatically and ensures consistent environment across different systems.

```bash
# Build and start the application
docker-compose up --build

# Run in background
docker-compose up -d --build
```

✅ **Ready!** API available at `http://127.0.0.1:8000`

### 🐍 Option 2: Local Development

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start development server
uvicorn app.main:app --reload
```

✅ **Ready!** API available at `http://127.0.0.1:8000`

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: `http://127.0.0.1:8000/docs` (recommended)
- **ReDoc**: `http://127.0.0.1:8000/redoc`

### API Workflow

The Chef AI API follows a simple session-based workflow:

```mermaid
graph TD
    A[Start Session] --> B[Upload Ingredients]
    B --> C[Get 3 Recipe Options]
    C --> D[Select Recipe]
    D --> E[Chat with AI]
    E --> F[Ask Questions]
    F --> E
    E --> G[End Session]
```

### Endpoints Overview

| Method | Endpoint | Description | Request Type |
|--------|----------|-------------|--------------|
| `POST` | `/api/session/` | **Create Session**: Upload ingredients (text/image) and get recipes | `multipart/form-data` |
| `POST` | `/api/session/{context_id}/select` | **Select Recipe**: Choose from generated recipes | `application/json` |
| `POST` | `/api/session/{context_id}/chat` | **Chat**: Ask questions about selected recipe | `application/json` |
| `DELETE` | `/api/session/{context_id}` | **End Session**: Clean up session data | - |

### Example Usage

#### 1. Start a Session with Ingredients

**Text Input:**
```bash
curl -X POST "http://127.0.0.1:8000/api/session/" \
  -F "ingredients_text=chicken breast, broccoli, garlic, soy sauce"
```

**Image Upload:**
```bash
curl -X POST "http://127.0.0.1:8000/api/session/" \
  -F "ingredients_image=@fridge_photo.jpg"
```

#### 2. Select a Recipe
```bash
curl -X POST "http://127.0.0.1:8000/api/session/{context_id}/select" \
  -H "Content-Type: application/json" \
  -d '{"recipe_id": 1}'
```

#### 3. Chat with AI
```bash
curl -X POST "http://127.0.0.1:8000/api/session/{context_id}/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "How long should I marinate the chicken?"}'
```

## 🏗️ Architecture

### Project Structure
```
chef-ai/
├── app/
│   ├── main.py              # FastAPI application entry point
│   ├── routers/             # API route handlers
│   ├── services/            # Business logic layer
│   ├── models/              # Database models
│   ├── schemas/             # Pydantic data models
│   └── utils/               # Utility functions
├── requirements.txt         # Python dependencies
├── docker-compose.yml       # Docker configuration
├── Dockerfile              # Container definition
└── .env.example            # Environment template
```

### Design Principles
- **Separation of Concerns**: Clear boundaries between routing, business logic, and data
- **Dependency Injection**: Loose coupling for better testability
- **Type Safety**: Full Pydantic validation and type hints
- **Scalable**: Modular architecture supports easy feature additions

## 📊 Project Assessment

### 👍 **Strengths**

**🎯 Robust AI Control**
- Advanced prompt engineering ensures reliable, focused AI behavior
- Resistant to manipulation and off-topic conversations
- Consistent persona across all interactions

**🏗️ Clean Architecture**
- Well-structured codebase with clear separation of concerns
- Easy to understand, maintain, and extend
- Modern Python best practices throughout

**⚡ Efficient Design**
- Single multimodal AI model handles all tasks
- Smart image preprocessing reduces API costs
- Optimized for performance and resource usage

**🔧 Developer Experience**
- Comprehensive API documentation
- Docker support for easy setup
- RESTful design with proper HTTP semantics

### 👎 **Areas for Improvement**

**🗄️ Database Scalability**
- Current SQLite setup ideal for development
- **Production consideration**: Migrate to PostgreSQL for high-concurrency scenarios

**🔄 State Management**
- In-memory rate limiting doesn't persist across restarts
- **Scaling consideration**: Implement Redis for shared state management

**🔐 Security**
- No authentication layer currently implemented
- **Production requirement**: Add JWT/OAuth2 authentication system

**🌐 Language Detection**
- Basic keyword-based language detection
- **Enhancement opportunity**: Integrate dedicated language detection library

## 🛣️ Roadmap

### Phase 1: Core Enhancements
- [ ] PostgreSQL integration
- [ ] Redis-based rate limiting
- [ ] Enhanced error handling

### Phase 2: Security & Auth
- [ ] JWT authentication
- [ ] User management system
- [ ] API key management

### Phase 3: Advanced Features
- [ ] Recipe rating system
- [ ] Ingredient substitution suggestions
- [ ] Nutritional information integration

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines for details on how to:
- Report bugs
- Suggest features
- Submit pull requests

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: Check the `/docs` endpoint when running
- **Issues**: Report bugs via GitHub Issues
- **Questions**: Start a discussion in GitHub Discussions

---

<div align="center">

**Built with ❤️ for home cooks everywhere**

[Documentation](http://127.0.0.1:8000/docs) • [API Reference](http://127.0.0.1:8000/redoc) • [Contributing](#contributing)

</div>