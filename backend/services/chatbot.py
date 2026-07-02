import requests
import os

try:
    import google.generativeai as genai
    from google.oauth2 import service_account

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    SERVICE_ACCOUNT_FILE = os.path.join(os.path.dirname(BASE_DIR), "service_account.json")
    SCOPES = ["https://www.googleapis.com/auth/generative-language"]

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    genai.configure(credentials=credentials)
    GEMINI_AVAILABLE = True
except Exception as e:
    print(f"Gemini not available: {e}")
    GEMINI_AVAILABLE = False

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3"

def check_ollama_status():
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3)
        return response.status_code == 200
    except:
        return False

def generate_chat_title(first_message: str) -> str:
    if len(first_message) <= 40:
        return first_message
    return first_message[:37] + "..."

def generate_ai_response(user_message: str, conversation_history=None) -> str:
    if GEMINI_AVAILABLE:
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            history = []
            for msg in (conversation_history or [])[-10:]:
                role = "user" if msg["role"] == "user" else "model"
                history.append({"role": role, "parts": [msg["content"]]})
            chat = model.start_chat(history=history)
            response = chat.send_message(user_message)
            return response.text
        except Exception as e:
            print(f"Gemini failed, falling back to Ollama: {e}")

    try:
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": user_message,
            "stream": False,
            "options": {"temperature": 0.7, "num_predict": 1024}
        }
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=300
        )
        result = response.json()
        return result.get("response", "").strip()
    except Exception as e:
        raise RuntimeError(f"Both Gemini and Ollama failed: {str(e)}")