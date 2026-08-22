import uuid
import shutil
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
from app.config import settings

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
    "image/gif",
}

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}

# Default avatar placeholder (SVG data URI or high-res default)
DEFAULT_AVATAR_URL = "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150"

def save_image_upload(file: UploadFile, subfolder: str = "avatars") -> str:
    """
    Strictly validates that an uploaded file is an image (JPEG/PNG/WebP/GIF)
    and saves it to the specified uploads subfolder with a safe unique UUID name.
    
    Returns the relative public URL path (e.g. '/uploads/avatars/abc12345.png').
    """
    if not file or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file was provided for upload."
        )
    
    # 1. Validate content type
    content_type = (file.content_type or "").lower()
    if content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type '{file.content_type}'. Only image files (JPEG, PNG, WebP, GIF) are allowed."
        )
    
    # 2. Validate file extension
    original_ext = Path(file.filename).suffix.lower()
    if original_ext not in ALLOWED_EXTENSIONS:
        # Fallback to extension based on content_type
        if "png" in content_type:
            original_ext = ".png"
        elif "webp" in content_type:
            original_ext = ".webp"
        elif "gif" in content_type:
            original_ext = ".gif"
        else:
            original_ext = ".jpg"
            
    # 3. Generate secure unique filename
    filename = f"{uuid.uuid4().hex}{original_ext}"
    target_dir = settings.UPLOAD_DIR / subfolder
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / filename
    
    # 4. Save file to disk
    try:
        with open(target_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save uploaded image: {str(e)}"
        )
        
    return f"/uploads/{subfolder}/{filename}"
