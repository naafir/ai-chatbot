from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from database import engine, Base
from routes.auth_routes import router as auth_router
from routes.chat_routes import router as chat_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get absolute paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "frontend"))
STATIC_DIR = os.path.join(FRONTEND_DIR, "static")
TEMPLATES_DIR = os.path.join(FRONTEND_DIR, "templates")

print(f"Static dir: {STATIC_DIR}")
print(f"Static exists: {os.path.exists(STATIC_DIR)}")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(chat_router, prefix="/api/chat", tags=["Chat"])

@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(TEMPLATES_DIR, "index.html"))

@app.get("/login")
async def serve_login():
    return FileResponse(os.path.join(TEMPLATES_DIR, "login.html"))

@app.get("/signup")
async def serve_signup():
    return FileResponse(os.path.join(TEMPLATES_DIR, "signup.html"))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "AI Chatbot API is running"}