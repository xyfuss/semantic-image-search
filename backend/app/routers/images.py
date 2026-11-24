from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
import uuid

from app.database import get_db
from app.storage import (
    create_presigned_get,
    create_presigned_put,
    object_size,
    delete_object,
)
from app.schemas import ImageSignRequest, ImageSignResponse, ImageCreate, ImageOut
from app.dependencies import get_current_user
from app.models import Image, User
from app.queue import queue
from app.embedding import embed_text

router = APIRouter(prefix="/images", tags=["images"])

MAX_SIZE = 10 * 1024 * 1024
ALLOWED_TYPES = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}


# helper
def to_image_out(image):
    return ImageOut(
        id=image.id,
        status=image.status,
        created_at=image.created_at,
        url=create_presigned_get(image.storage_key),
    )


@router.post("/sign", response_model=ImageSignResponse)
def sign(data: ImageSignRequest, current_user: User = Depends(get_current_user)):

    if data.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, "Unsupported media type."
        )

    if data.size > MAX_SIZE:
        raise HTTPException(
            status.HTTP_413_CONTENT_TOO_LARGE, "Invalid file size (Max 10MB)."
        )

    key = f"{current_user.id}/{uuid.uuid4().hex}.{ALLOWED_TYPES[data.content_type]}"

    return ImageSignResponse(
        upload_url=create_presigned_put(key, data.content_type), storage_key=key
    )


@router.post("/complete", response_model=ImageOut, status_code=status.HTTP_201_CREATED)
def complete(
    data: ImageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    if not data.storage_key.startswith(f"{current_user.id}/"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not your upload.")

    size = object_size(data.storage_key)

    if size is None:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Upload not found.")

    if size > MAX_SIZE:
        delete_object(data.storage_key)
        raise HTTPException(
            status.HTTP_413_CONTENT_TOO_LARGE, "Invalid file size (Max 10MB)."
        )

    if db.scalar(select(Image).where(Image.storage_key == data.storage_key)):
        raise HTTPException(status.HTTP_409_CONFLICT, "Image already exists.")

    image = Image(user_id=current_user.id, storage_key=data.storage_key)

    db.add(image)
    db.commit()
    db.refresh(image)
    queue.enqueue("app.jobs.process_image", image.id)

    return to_image_out(image)


@router.get("", response_model=list[ImageOut])
def list_images(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):

    images = db.scalars(
        select(Image)
        .where(Image.user_id == current_user.id)
        .order_by(Image.created_at.desc())
    ).all()

    return [to_image_out(img) for img in images]


@router.get("/search", response_model=list[ImageOut])
def search(
    query: str = Query(min_length=1, max_length=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query_vec = embed_text(query)
    images = db.scalars(
        select(Image)
        .where(Image.user_id == current_user.id, Image.status == "ready")
        .order_by(Image.embedding.cosine_distance(query_vec))
        .limit(20)
    ).all()

    return [to_image_out(img) for img in images]


@router.delete("/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_img(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    image = db.scalar(
        select(Image).where(Image.id == image_id, Image.id == current_user.id)
    )

    if image is None or image.id != current_user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Image not found.")

    storage_key = image.storage_key

    db.delete(image)
    db.commit()
    delete_object(storage_key)
