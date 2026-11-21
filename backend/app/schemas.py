from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime

class OrmModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=8)

    @field_validator("username")
    @classmethod
    def strip_name(cls, v: str) -> str:
        return v.strip()

    @field_validator("password")
    @classmethod
    def byte_check(cls, v: str) -> str:
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Password must be at most 72 bytes.")
        return v


class UserOut(OrmModel):
    username: str
    id: int

class ImageCreate(BaseModel):
    storage_key: str = Field(pattern=r"^[0-9a-f]{32}\.(jpg|png|webp)$")

class ImageOut(OrmModel):
    id: int
    status: str
    created_at: datetime

class ImageSignRequest(BaseModel):
    content_type: str
    size: int = Field(gt=0)

class ImageSignResponse(BaseModel):
    upload_url: str
    storage_key: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserLogin(BaseModel):
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=8)
