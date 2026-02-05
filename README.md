# AI-Powered Support Ticket Backend

![FastAPI](https://img.shields.io/badge/FastAPI-000000?style=flat&logo=fastapi&logoColor=white)
![MongoDB](https://img.shields.io/badge/MongoDB-47A248?style=flat&logo=mongodb&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-89C53C?style=flat&logo=celery&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-DC382D?style=flat&logo=redis&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-000000?style=flat&logo=python&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat&logo=openai&logoColor=white)

---

## 🔥 Project Overview

A **production-ready backend system** that combines modern backend architecture with **AI-driven ticket automation**, designed to demonstrate industry-standard backend skills:

- Asynchronous REST API with **FastAPI**  
- NoSQL storage with **MongoDB**  
- Secure authentication using **JWT**  
- Background task processing with **Celery + Redis**  
- AI-driven ticket summarization and categorization using **LangChain + OpenAI GPT**  
- Fully containerized deployment with **Docker Compose**

---

## 🏗 Architecture Overview

```
+-------------------+        +-------------------+
|    FastAPI API     | <----> |    MongoDB DB     |
| (REST Endpoints)   |        | (Async Storage)   |
+---------+---------+        +-------------------+
          |
          v
    +-------------------+
    | Celery Worker      |
    | (Background Tasks) |
    +---------+---------+
              |
              v
        +-------------+
        |  LangChain  |
        |   + LLM     |
        +-------------+
```

**Flow:**

1. Client requests ticket creation via FastAPI  
2. Ticket stored in MongoDB  
3. Celery triggers **LangChain** task asynchronously  
4. LLM generates:
   - Ticket summary  
   - Ticket category  
   - Suggested reply  
5. Result updated back in MongoDB  
6. User retrieves AI-enhanced ticket asynchronously  

---

## 🛠 Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| API | FastAPI | Async REST API framework |
| Database | MongoDB | NoSQL document storage |
| Auth | JWT + Passlib | Secure authentication & password hashing |
| Background Processing | Celery + Redis | Async AI tasks |
| AI Service | LangChain + OpenAI | LLM-powered ticket analysis |
| Containerization | Docker + Docker Compose | Multi-service orchestration |
| Language | Python 3.11 | Backend logic |

---

## ⚡ Features

- **User Management**  
  - Register, Login, JWT-based authentication  

- **Ticket Management**  
  - Create, List tickets  
  - Async AI processing (summary, category, suggested reply)  

- **AI Integration**  
  - LangChain handles prompt engineering and AI orchestration  
  - OpenAI GPT model for LLM inference  

- **Production-Ready**  
  - Fully containerized  
  - Async, non-blocking design  
  - Modular, maintainable folder structure  

---

## 📁 Folder Structure

```
ai-ticket-backend/
│── app/
│   │── main.py               # FastAPI app
│   │── core/
│   │   │── config.py
│   │   │── security.py       # JWT & password hashing
│   │   │── dependencies.py   # Protected routes
│   │── db/
│   │   │── mongodb.py
│   │   │── crud.py
│   │── models/
│   │   │── user.py
│   │   │── ticket.py
│   │── schemas/
│   │   │── user_schema.py
│   │   │── ticket_schema.py
│   │── routes/
│   │   │── auth_routes.py
│   │   │── ticket_routes.py
│   │── tasks/
│   │   │── celery_app.py
│   │   │── ticket_tasks.py
│── tests/                   # Pytest tests (optional)
│── docker-compose.yml
│── Dockerfile
│── requirements.txt
│── .env
│── README.md
```

---

## ⚡ Setup & Running

### 1️⃣ Clone the repo

```bash
git clone https://github.com/your-username/ai-ticket-backend.git
cd ai-ticket-backend
```

### 2️⃣ Environment Variables

Create `.env`:

```env
MONGO_URI=mongodb://mongo:27017
REDIS_URL=redis://redis:6379/0
OPENAI_API_KEY=sk-your-openai-key
SECRET_KEY=supersecretkey123
```

### 3️⃣ Build & Run (Docker Compose)

```bash
docker compose up --build
```

This will start:

- FastAPI API → http://localhost:8000/docs  
- MongoDB → port 27017  
- Redis → port 6379  
- Celery Worker → handles async AI tasks  

---

## 🧪 API Endpoints

| Endpoint | Method | Description | Auth |
|----------|--------|------------|------|
| `/auth/register` | POST | Register new user | ❌ |
| `/auth/login` | POST | Login user, returns JWT | ❌ |
| `/tickets` | POST | Create new ticket | ✅ |
| `/tickets` | GET | List tickets for current user | ✅ |

---

### Example Workflow

1. **Register User**

```json
POST /auth/register
{
  "email": "user@example.com",
  "password": "secret123"
}
```

2. **Login**

```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded
username=user@example.com
password=secret123
```

Response:

```json
{
  "access_token": "<JWT_TOKEN>",
  "token_type": "bearer"
}
```

3. **Create Ticket**

```json
POST /tickets
Authorization: Bearer <JWT_TOKEN>
{
  "title": "Cannot login",
  "description": "Forgot password, cannot access account"
}
```

Celery triggers **LangChain task** → AI fills summary, category, suggested reply.

---

## ⚡ Next Enhancements (Optional)

- Add **unit tests** with `pytest`  
- Add **admin panel API** for ticket moderation  
- Add **logging, monitoring, and metrics** (e.g., Prometheus, Flower for Celery)  
- Swap OpenAI with **local LLM** for fully self-hosted AI  

---

## 🚀 Author

**Mohammad Jalili** – Software Engineer (Backend / Applied ML) 

