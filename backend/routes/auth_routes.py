"""
Authentication Routes
Endpoints:
  POST /api/auth/signup  â€” Register a new user
  POST /api/auth/login   â€” Login and receive JWT token
  GET  /api/auth/me      â€” Get current user profile
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models import User
from auth.auth import hash_password, verify_password, create_access_token, get_current_user
from utils.schemas import SignupRequest, LoginRequest, AuthResponse, UserResponse

router = APIRouter()


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """
    Register a new user account.
    - Validates username and email uniqueness
    - Hashes password before storing
    - Returns JWT token immediately (auto-login after signup)
    """
    # Check if email already exists
    existing_email = db.query(User).filter(User.email == request.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists"
        )

    # Check if username already exists
    existing_username = db.query(User).filter(User.username == request.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This username is already taken"
        )

    # Create new user with hashed password
    new_user = User(
        username=request.username,
        email=request.email,
        password_hash=hash_password(request.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate JWT token for immediate login
    token = create_access_token(data={"sub": str(new_user.id)})

    return AuthResponse(
        access_token=token,
        user_id=new_user.id,
        username=new_user.username,
        email=new_user.email
    )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate a user and return a JWT token.
    - Looks up user by email
    - Verifies bcrypt password hash
    - Returns JWT token valid for 7 days
    """
    # Find user by email
    user = db.query(User).filter(User.email == request.email).first()

    # Generic error message prevents email enumeration attacks
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Generate JWT token
    token = create_access_token(data={"sub": str(user.id)})

    return AuthResponse(
        access_token=token,
        user_id=user.id,
        username=user.username,
        email=user.email
    )


@router.get("/me", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_user)):
    """
    Get the currently authenticated user's profile.
    Requires: Authorization: Bearer <token> header.
    """
    return current_user


