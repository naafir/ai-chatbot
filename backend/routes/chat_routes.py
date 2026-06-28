"""
Chat Routes
Endpoints:
  POST   /api/chat/message        â€” Send a message and get AI response
  GET    /api/chat/history        â€” List all chats for current user
  GET    /api/chat/{chat_id}      â€” Get a specific chat with messages
  DELETE /api/chat/{chat_id}      â€” Delete a chat and all its messages
  GET    /api/chat/status/ollama  â€” Check if Ollama is running
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import User, Chat, Message
from auth.auth import get_current_user
from services.chatbot import generate_ai_response, generate_chat_title, check_ollama_status
from utils.schemas import (
    SendMessageRequest, SendMessageResponse,
    ChatResponse, ChatWithMessagesResponse,
    MessageResponse, DeleteChatResponse
)

router = APIRouter()


@router.post("/message", response_model=SendMessageResponse)
async def send_message(
    request: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send a user message and receive an AI-generated response.

    Flow:
    1. Create new chat or load existing chat
    2. Fetch conversation history for context
    3. Call Ollama to generate AI response
    4. Save both user and AI messages to database
    5. Return both messages to the frontend
    """
    # â”€â”€ Step 1: Get or create the chat â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    if request.chat_id:
        # Load existing chat â€” verify it belongs to current user
        chat = db.query(Chat).filter(
            Chat.id == request.chat_id,
            Chat.user_id == current_user.id
        ).first()
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat not found"
            )
    else:
        # Create a new chat with a title from the first message
        title = generate_chat_title(request.message)
        chat = Chat(user_id=current_user.id, title=title)
        db.add(chat)
        db.commit()
        db.refresh(chat)

    # â”€â”€ Step 2: Fetch recent conversation history â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    existing_messages = db.query(Message).filter(
        Message.chat_id == chat.id
    ).order_by(Message.timestamp).all()

    history = [{"role": msg.role, "content": msg.content} for msg in existing_messages]

    # â”€â”€ Step 3: Generate AI response via Ollama â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    try:
        ai_response_text = generate_ai_response(
            user_message=request.message,
            conversation_history=history
        )
    except ConnectionError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

    # â”€â”€ Step 4: Save messages to database â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    user_msg = Message(
        chat_id=chat.id,
        role="user",
        content=request.message
    )
    db.add(user_msg)

    ai_msg = Message(
        chat_id=chat.id,
        role="assistant",
        content=ai_response_text
    )
    db.add(ai_msg)
    db.commit()
    db.refresh(user_msg)
    db.refresh(ai_msg)

    # â”€â”€ Step 5: Return response â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    return SendMessageResponse(
        chat_id=chat.id,
        user_message=MessageResponse.from_orm(user_msg),
        ai_message=MessageResponse.from_orm(ai_msg),
        chat_title=chat.title
    )


@router.get("/history", response_model=List[ChatResponse])
async def get_chat_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns a list of all chat sessions for the logged-in user,
    ordered by most recent first.
    """
    chats = db.query(Chat).filter(
        Chat.user_id == current_user.id
    ).order_by(Chat.created_at.desc()).all()

    return chats


@router.get("/{chat_id}", response_model=ChatWithMessagesResponse)
async def get_chat(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns a single chat session with all its messages.
    Only accessible by the chat's owner.
    """
    chat = db.query(Chat).filter(
        Chat.id == chat_id,
        Chat.user_id == current_user.id
    ).first()

    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )

    return chat


@router.delete("/{chat_id}", response_model=DeleteChatResponse)
async def delete_chat(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Permanently delete a chat and all its messages.
    Cascade delete is handled by SQLAlchemy relationship.
    """
    chat = db.query(Chat).filter(
        Chat.id == chat_id,
        Chat.user_id == current_user.id
    ).first()

    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found"
        )

    db.delete(chat)
    db.commit()

    return DeleteChatResponse(success=True, message="Chat deleted successfully")


@router.get("/status/ollama")
async def ollama_status():
    """Check whether Ollama is running and accessible."""
    is_running = check_ollama_status()
    return {
        "ollama_running": is_running,
        "message": "Ollama is running" if is_running else "Ollama is not running. Start it with: ollama serve"
    }


