"""
Chatbot Service â€” Ollama Integration
Handles communication with Ollama's local API to generate AI responses
using the Llama 3 model (completely free, runs offline).

Ollama API endpoint: http://localhost:11434/api/generate
"""

import requests
import json
from typing import List, Dict

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3"

# System prompt â€” defines the AI's personality and behavior
SYSTEM_PROMPT = """You are a helpful, knowledgeable, and friendly AI assistant.
You provide clear, accurate, and thoughtful responses to user questions.
You are honest about what you know and don't know.
When answering technical questions, you provide code examples when appropriate.
Keep your responses concise yet comprehensive."""


def check_ollama_status() -> bool:
    """Check if Ollama service is running locally."""
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=3)
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        return False


def format_conversation_history(messages: List[Dict]) -> str:
    """
    Format previous chat messages as a conversation string
    to provide context to the AI model.

    Args:
        messages: List of {"role": "user"/"assistant", "content": "..."} dicts
    Returns:
        Formatted conversation string
    """
    if not messages:
        return ""

    conversation = ""
    for msg in messages[-10:]:  # Use last 10 messages for context window
        role = "Human" if msg["role"] == "user" else "Assistant"
        conversation += f"{role}: {msg['content']}\n\n"
    return conversation


def generate_ai_response(
    user_message: str,
    conversation_history: List[Dict] = None
) -> str:
    """
    Send a message to Ollama's Llama 3 model and get a response.

    Args:
        user_message: The user's current message
        conversation_history: Previous messages for context

    Returns:
        AI-generated response string

    Raises:
        ConnectionError: If Ollama is not running
        RuntimeError: If Ollama returns an error
    """

    # Check if Ollama is running
    if not check_ollama_status():
        raise ConnectionError(
            "Ollama is not running. Please start Ollama with: ollama serve"
        )

    # Build the full prompt with system context and conversation history
    history_str = format_conversation_history(conversation_history or [])

    full_prompt = f"""{SYSTEM_PROMPT}

{f"Previous conversation:{chr(10)}{history_str}" if history_str else ""}
Human: {user_message}
Assistant:"""

    # Prepare request payload for Ollama API
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": full_prompt,
        "stream": False,        # Get complete response at once
        "options": {
            "temperature": 0.7,     # Creativity level (0=deterministic, 1=creative)
            "top_p": 0.9,           # Nucleus sampling
            "top_k": 40,            # Top-k sampling
            "num_predict": 1024,    # Max tokens in response
        }
    }

    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=120  # 2 minute timeout for AI generation
        )

        if response.status_code != 200:
            raise RuntimeError(f"Ollama returned status {response.status_code}: {response.text}")

        result = response.json()
        ai_response = result.get("response", "").strip()

        if not ai_response:
            raise RuntimeError("Ollama returned an empty response")

        return ai_response

    except requests.exceptions.Timeout:
        raise RuntimeError(
            "Request to Ollama timed out. The model may be loading. Please try again."
        )
    except requests.exceptions.ConnectionError:
        raise ConnectionError(
            "Cannot connect to Ollama. Make sure Ollama is running: ollama serve"
        )
    except json.JSONDecodeError:
        raise RuntimeError("Invalid response from Ollama API")


def generate_chat_title(first_message: str) -> str:
    """
    Generate a short title for a new chat based on the first user message.
    Falls back to a truncated version of the message if Ollama is unavailable.

    Args:
        first_message: The user's first message in the chat
    Returns:
        Short descriptive title string
    """
    # Simple fallback: truncate the first message
    if len(first_message) <= 40:
        return first_message
    return first_message[:37] + "..."


