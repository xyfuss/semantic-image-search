from fastapi import APIRouter, Depends, HTTPException, status
import uuid

from app.storage import create_presigned_key
from app.schemas import ImageSignRequest, ImageSignResponse

router = APIRouter(prefix="/images", tags=["images"])

ALLOWED_TYPES = {'image/jpg': 'jpg', 'image/png': 'png', 'image/webp': 'webp'}

@router.post('/sign', response_model=ImageSignResponse)
def sign(data: ImageSignRequest, current_user: User = Depends(get_current_user)):
    if data.content_type not in ALLOWED_TYPES:
        raise HTTPException(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Unsupported media type.")
    if data.size > (10 * 1024 * 1024):
        raise HTTPException(status.HTTP_413_CONTENT_TOO_LARGE, "Invalid file size (Max 50MB).")
    key = f"{uuid.uuid4().hex}.{ALLOWED_TYPES[data.content_type]}"
    return ImageSignResponse(upload_url=create_presigned_put(key, data.content_type), storage_key=key)


