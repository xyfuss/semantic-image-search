import io

from PIL import Image as PILImage
from sqlalchemy import select

from app.database import SessionLocal
from app.embedding import embed_image
from app.models import Image
from app.storage import download_object


def process_image(image_id: int) -> None:
    db = SessionLocal()
    try:
        image = db.get(Image, image_id)
        if image is None:
            return
        try:
            data = download_object(image.storage_key)
            pil_image = PILImage.open(io.BytesIO(data)).convert("RGB")
            image.embedding = embed_image(pil_image)
            image.status = "ready"
            db.commit()
        except Exception:
            db.rollback()
            image.status = "failed"
            db.commit()
            raise
    finally:
        db.close()
