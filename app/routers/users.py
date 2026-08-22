from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.routers.auth import get_current_user
from app.utils.security import get_password_hash
from app.utils.upload import save_image_upload

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/profile", response_model=UserResponse, summary="Get current user profile")
def get_user_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/profile", response_model=UserResponse, summary="Update current user profile")
def update_user_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if update_data.full_name is not None:
        current_user.full_name = update_data.full_name
    if update_data.avatar_url is not None:
        current_user.avatar_url = update_data.avatar_url
    if update_data.email is not None:
        # Check if email is already taken
        existing = db.query(User).filter(User.email == update_data.email, User.id != current_user.id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email is already in use by another account")
        current_user.email = update_data.email
    if update_data.password is not None:
        current_user.password_hash = get_password_hash(update_data.password)

    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/avatar", response_model=UserResponse, summary="Upload avatar image from device")
def upload_avatar(
    file: UploadFile = File(..., description="Image file from device (JPEG, PNG, WebP, GIF)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload an avatar image directly from device.
    Only image files (JPEG, PNG, WebP, GIF) are allowed.
    """
    avatar_url = save_image_upload(file, subfolder="avatars")
    current_user.avatar_url = avatar_url
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/{user_id}", response_model=UserResponse, summary="Get public user info by ID")
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
