import bcrypt


def hash_password(pw: str) -> str:
    hashed = bcrypt.hashpw(pw.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")

def verify_password(pw: str,pw_hash: str) -> bool:
    return bcrypt.checkpw(
        pw.encode("utf-8"), pw_hash.encode("utf-8")
    )