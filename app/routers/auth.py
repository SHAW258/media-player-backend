from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.auth import Token, LoginRequest, RegisterRequest
from app.schemas.user import UserResponse
from app.utils.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
    oauth2_scheme
)
from app.utils.upload import save_image_upload, DEFAULT_AVATAR_URL

router = APIRouter(prefix="/auth", tags=["Authentication"])

def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Dependency to retrieve authenticated user from JWT token."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = int(payload["sub"])
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )
    return user

def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Optional authentication dependency; returns None if unauthenticated."""
    if not token:
        return None
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        return None
    try:
        user_id = int(payload["sub"])
        return db.query(User).filter(User.id == user_id).first()
    except Exception:
        return None

def validate_credentials_for_signup(username: str, email: str, password: str, confirm_password: Optional[str], db: Session):
    """Validates password length, confirmation match, and case-insensitive unique username/email."""
    username_clean = username.strip()
    if len(username_clean) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must be at least 3 characters long."
        )
        
    if len(password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters long."
        )
        
    if confirm_password is not None and password != confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match. Please ensure password and confirm password are identical."
        )
        
    # Case-insensitive duplicate username check
    existing_username = db.query(User).filter(func.lower(User.username) == username_clean.lower()).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Username '{username_clean}' is already taken. Please choose another username."
        )
        
    # Case-insensitive duplicate email check
    email_clean = str(email).strip().lower()
    existing_email = db.query(User).filter(func.lower(User.email) == email_clean).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )
        
    return username_clean, email_clean

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED, summary="Register a new user")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Create a new user account and return an access token."""
    username_clean, email_clean = validate_credentials_for_signup(
        username=request.username,
        email=request.email,
        password=request.password,
        confirm_password=request.confirm_password,
        db=db
    )
    
    new_user = User(
        username=username_clean,
        email=email_clean,
        password_hash=get_password_hash(request.password),
        full_name=request.full_name or "John Doe",
        avatar_url=request.avatar_url or DEFAULT_AVATAR_URL,
        role="user",
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token(data={"sub": str(new_user.id), "username": new_user.username, "role": new_user.role})
    return Token(
        access_token=token,
        token_type="bearer",
        user_id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        full_name=new_user.full_name,
        avatar_url=new_user.avatar_url,
        role=new_user.role
    )

@router.post("/register-with-avatar", response_model=Token, status_code=status.HTTP_201_CREATED, summary="Register new user with direct avatar image upload from device")
def register_with_avatar(
    username: str = Form(..., description="Unique username (min 3 chars)"),
    email: str = Form(..., description="Valid email address"),
    password: str = Form(..., description="Account password (min 6 chars)"),
    confirm_password: Optional[str] = Form(None, description="Confirm password (must match password)"),
    full_name: str = Form("John Doe", description="User full display name"),
    avatar: Optional[UploadFile] = File(None, description="Image file from device (JPEG, PNG, WebP, GIF)"),
    db: Session = Depends(get_db)
):
    """
    Create a new user account with an avatar image directly uploaded from device.
    Strictly validates image MIME types (JPEG, PNG, WebP, GIF) and password confirmation.
    """
    username_clean, email_clean = validate_credentials_for_signup(
        username=username,
        email=email,
        password=password,
        confirm_password=confirm_password,
        db=db
    )
    
    avatar_url = DEFAULT_AVATAR_URL
    if avatar and avatar.filename:
        avatar_url = save_image_upload(avatar, subfolder="avatars")
        
    new_user = User(
        username=username_clean,
        email=email_clean,
        password_hash=get_password_hash(password),
        full_name=full_name or "John Doe",
        avatar_url=avatar_url,
        role="user",
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token(data={"sub": str(new_user.id), "username": new_user.username, "role": new_user.role})
    return Token(
        access_token=token,
        token_type="bearer",
        user_id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        full_name=new_user.full_name,
        avatar_url=new_user.avatar_url,
        role=new_user.role
    )

@router.post("/login", response_model=Token, summary="Login with username/email and password")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return JWT bearer token."""
    user = db.query(User).filter(
        (User.username == request.username_or_email) | (User.email == request.username_or_email)
    ).first()

    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is inactive"
        )

    token = create_access_token(data={"sub": str(user.id), "username": user.username, "role": user.role})
    return Token(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        avatar_url=user.avatar_url,
        role=user.role
    )

@router.post("/token", response_model=Token, include_in_schema=False)
def login_for_swagger(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """OAuth2 compatible token login for Swagger UI 'Authorize' button."""
    user = db.query(User).filter(
        (User.username == form_data.username) | (User.email == form_data.username)
    ).first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(data={"sub": str(user.id), "username": user.username, "role": user.role})
    return Token(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        avatar_url=user.avatar_url,
        role=user.role
    )

@router.get("/me", response_model=UserResponse, summary="Get current logged-in user profile")
def get_me(current_user: User = Depends(get_current_user)):
    """Returns profile of currently authenticated user."""
    return current_user
