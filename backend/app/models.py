from datetime import datetime
from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship


from database import Base

class Image(Base):
    __tablename__ = "images"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    storage_key: Mapped[str] = mapped_column(unique=True)
    status: Mapped[str] = mapped_column(default="pending")
    embedding: Mapped[list[float] | None] = mapped_column(Vector(512))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    user: Mapped["User"] = relationship(back_populates="images")

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str] = mapped_column()
    images: Mapped[list["Image"]] = relationship(back_populates="user")