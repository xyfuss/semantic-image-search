import bcrypt
import jwt
from datetime import datetime, timedelta, timezone

from app.config import settings


def hash_password(pw: str) -> str:
    hashed = bcrypt.hashpw(pw.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(pw: str, pw_hash: str) -> bool:
    return bcrypt.checkpw(pw.encode("utf-8"), pw_hash.encode("utf-8"))


def create_access_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=60),
    }
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")
