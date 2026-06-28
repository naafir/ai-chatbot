# ⚡ AI Chat — Free Local ChatGPT Alternative

> A fully-featured, production-quality AI chatbot built with FastAPI, Ollama (Llama 3), and vanilla JavaScript.  
> **100% free. No API keys. Runs entirely on your computer.**

![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg)
![Ollama](https://img.shields.io/badge/Ollama-Llama3-orange.svg)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Screenshots](#screenshots)
- [Future Improvements](#future-improvements)
- [Deploy Online for Free](#deploy-online-for-free)
- [Common Errors & Fixes](#common-errors--fixes)

---

## 🎯 Overview

AI Chat is a ChatGPT-like web application that runs **completely free and offline** on your local machine. It uses:

- **Ollama** to run the **Llama 3** language model locally (no GPU required for smaller models)
- **FastAPI** as the backend REST API with JWT authentication
- **SQLite** for persistent storage of users, chats, and messages
- **Vanilla HTML/CSS/JS** for a modern, responsive frontend

Perfect for college portfolios, internship projects, or personal use.

---

## ✨ Features

| Feature | Status |
|---|---|
| 💬 ChatGPT-like chat interface | ✅ |
| 🔐 User signup & login (JWT) | ✅ |
| 📜 Persistent chat history | ✅ |
| 🗑️ Delete individual chats | ✅ |
| 🌑 Dark mode design | ✅ |
| 📱 Responsive (mobile-friendly) | ✅ |
| ⚡ Typing animation indicator | ✅ |
| 🦙 Llama 3 AI (via Ollama) | ✅ |
| 🔒 Password hashing (bcrypt) | ✅ |
| 📋 Sidebar chat history | ✅ |
| ✨ Suggestion cards | ✅ |
| 🟢 Ollama status indicator | ✅ |
| 💻 Code block formatting | ✅ |
| 🚪 Logout | ✅ |

---

## 🛠 Tech Stack

### Backend
| Tech | Purpose |
|---|---|
| Python 3.10+ | Language |
| FastAPI | REST API framework |
| SQLAlchemy | ORM (Object-Relational Mapping) |
| SQLite | Database |
| Passlib (bcrypt) | Password hashing |
| python-jose | JWT token creation/validation |
| Uvicorn | ASGI server |

### Frontend
| Tech | Purpose |
|---|---|
| HTML5 | Structure |
| CSS3 (custom properties) | Styling |
| Vanilla JavaScript (ES2022) | Logic |
| Google Fonts (Inter) | Typography |

### AI
| Tech | Purpose |
|---|---|
| Ollama | Local LLM runner |
| Llama 3 | AI language model |

---

## 📁 Project Structure

```
ai-chatbot/
│
├── backend/                    # FastAPI backend
│   ├── app.py                  # Main application, routers, CORS
│   ├── database.py             # SQLAlchemy engine & session
│   ├── models.py               # ORM models (User, Chat, Message)
│   ├── auth/
│   │   ├── __init__.py
│   │   └── auth.py             # JWT + password hashing
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth_routes.py      # Signup, Login, Profile endpoints
│   │   └── chat_routes.py      # Send, History, Load, Delete endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   └── chatbot.py          # Ollama API integration
│   └── utils/
│       ├── __init__.py
│       └── schemas.py          # Pydantic request/response schemas
│
├── frontend/
│   ├── templates/
│   │   ├── index.html          # Main chat interface
│   │   ├── login.html          # Login page
│   │   └── signup.html         # Registration page
│   └── static/
│       ├── css/
│       │   └── style.css       # Complete stylesheet (dark theme)
│       └── js/
│           └── app.js          # All frontend logic
│
├── database/
│   ├── schema.sql              # SQL schema reference
│   └── chatbot.db              # SQLite database (auto-created)
│
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
├── .gitignore
├── start.sh                    # Linux/Mac startup script
├── start.bat                   # Windows startup script
└── README.md                   # This file
```

---

## 🚀 Installation

### Prerequisites

- Python 3.10 or higher
- pip (comes with Python)
- [Ollama](https://ollama.ai) (for AI responses)
- A modern web browser

---

### Step 1 — Clone / Download the Project

```bash
# If using Git:
git clone https://github.com/yourusername/ai-chatbot.git
cd ai-chatbot

# Or just extract the zip and cd into the folder
```

---

### Step 2 — Install Ollama

**On macOS / Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**On Windows:**
Download the installer from [https://ollama.ai](https://ollama.ai) and run it.

---

### Step 3 — Pull the Llama 3 Model

This downloads the Llama 3 model (~4.7 GB for the 8B version):

```bash
ollama pull llama3
```

> 💡 For computers with less RAM (< 8 GB), use the smaller model instead:
> ```bash
> ollama pull llama3:8b-instruct-q4_0
> ```
> Then update `OLLAMA_MODEL` in `backend/services/chatbot.py`

---

### Step 4 — Start Ollama

```bash
ollama serve
```

Leave this running in a separate terminal window.

---

### Step 5 — Create Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it:
# macOS / Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

---

### Step 6 — Install Python Dependencies

```bash
pip install -r requirements.txt
```

---

### Step 7 — Configure Environment

```bash
cp .env.example .env
```

Edit `.env` if you want to change the secret key (recommended for production):
```
SECRET_KEY=your-random-secret-key-here
```

---

### Step 8 — Run the Application

```bash
cd backend
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Or use the startup scripts:
```bash
# macOS / Linux:
bash start.sh

# Windows:
start.bat
```

---

### Step 9 — Open in Browser

Navigate to: **[http://localhost:8000](http://localhost:8000)**

1. Click **"Create Account"** to sign up
2. Log in with your credentials
3. Start chatting!

---

## 🎮 Usage

### Sending Messages
- Type in the input box at the bottom
- Press **Enter** to send (Shift+Enter for new line)
- Click the send button (arrow icon)

### Chat History
- All conversations are saved automatically
- Click any chat in the left sidebar to reload it
- Click the **✕** button on a chat to delete it

### New Chat
- Click the **"+ New Chat"** button in the sidebar

### Logout
- Click the **⋯** menu next to your name in the sidebar footer
- Select **"Sign Out"**

---

## 🔌 API Reference

Base URL: `http://localhost:8000/api`

Interactive docs: `http://localhost:8000/docs`

### Authentication

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| POST | `/auth/signup` | Register new user | No |
| POST | `/auth/login` | Login + get token | No |
| GET  | `/auth/me` | Get current user | Yes |

### Chat

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| POST | `/chat/message` | Send message + get AI reply | Yes |
| GET  | `/chat/history` | List all chats | Yes |
| GET  | `/chat/{chat_id}` | Get chat + messages | Yes |
| DELETE | `/chat/{chat_id}` | Delete a chat | Yes |
| GET | `/chat/status/ollama` | Ollama health check | No |

### Example: Send a Message

```bash
curl -X POST http://localhost:8000/api/chat/message \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is machine learning?"}'
```

---

## 📸 Screenshots

> Add screenshots here after running the project.

| Page | Description |
|---|---|
| `login.html` | Clean dark login page with animated background |
| `signup.html` | Registration with real-time validation |
| `index.html` | Full chat interface with sidebar history |
| Chat active | AI responses with code formatting |

---

## 🔮 Future Improvements

- [ ] **Streaming responses** — Show AI response token-by-token (like ChatGPT)
- [ ] **Model switcher** — Switch between Llama 3, Mistral, Phi-3 in the UI
- [ ] **Markdown rendering** — Full markdown support with marked.js
- [ ] **Export chat** — Download chat as PDF or text file
- [ ] **Voice input** — Speech-to-text using Web Speech API
- [ ] **Image upload** — Support multimodal models (LLaVA)
- [ ] **Chat search** — Full-text search across all conversations
- [ ] **Themes** — Light mode, custom accent colors
- [ ] **Rate limiting** — Prevent API abuse
- [ ] **Email verification** — Verify user emails on signup
- [ ] **Docker** — Containerize with docker-compose
- [ ] **System prompts** — Let users set custom AI personas

---

## 🌐 Deploy Online for Free

### Option 1: Railway (Easiest)
1. Push your code to GitHub
2. Go to [railway.app](https://railway.app)
3. Connect your GitHub repo
4. Add environment variable: `SECRET_KEY=your-key`
5. **Note:** Ollama won't run on Railway's free tier — switch to Groq API (free tier) for cloud deployment

### Option 2: Render
1. Push to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect repo, set build command: `pip install -r requirements.txt`
4. Set start command: `cd backend && uvicorn app:app --host 0.0.0.0 --port $PORT`

### Option 3: Self-host on a VPS
- Use Oracle Cloud Always Free tier (2 vCPUs, 1 GB RAM)
- Install Ollama + pull llama3
- Run with `systemd` service for auto-restart
- Use Nginx as reverse proxy

### Replacing Ollama for Cloud Deployment
For cloud hosting without GPU, use [Groq](https://console.groq.com) — it offers **free API access** to Llama 3.
Replace the Ollama call in `backend/services/chatbot.py` with:
```python
from groq import Groq
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
```

---

## 🐛 Common Errors & Fixes

### ❌ "Ollama is not running"
```
Solution: Open a terminal and run: ollama serve
Keep it running while using the app.
```

### ❌ "Connection refused" on port 8000
```
Solution: Make sure the FastAPI server is running.
Run: cd backend && python -m uvicorn app:app --reload
```

### ❌ "Model not found" / Ollama error
```
Solution: Pull the model first.
Run: ollama pull llama3
```

### ❌ "ModuleNotFoundError"
```
Solution: Activate your virtual environment first.
macOS/Linux: source venv/bin/activate
Windows:     venv\Scripts\activate
Then: pip install -r requirements.txt
```

### ❌ "422 Unprocessable Entity" on signup
```
Solution: Check your email format and that password is 6+ characters.
Username must use only letters, numbers, - and _
```

### ❌ Response is very slow
```
This is normal! Llama 3 on CPU takes 10–60 seconds per response.
For faster responses: use llama3:8b-instruct-q4_0 (smaller quantized model)
```

### ❌ Frontend shows "Ollama offline" even when running
```
Solution: Ollama is running but model not loaded.
Run: ollama pull llama3
```

---

## 🤝 Contributing

Pull requests welcome! For major changes, open an issue first.

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 👨‍💻 Built With

Made as a college portfolio project demonstrating:
- Full-stack web development
- REST API design
- Authentication & security
- AI/ML integration
- Database design
- UI/UX design

---

> ⭐ If this project helped you, consider giving it a star on GitHub!
