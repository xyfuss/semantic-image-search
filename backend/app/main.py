from fastapi import FastAPI

from app.routers import auth
from app.routers import images

app = FastAPI(title="Semantic Image Search")

app.include_router(auth.router)
app.include_router(images.router)


@app.get("/health")
def health():
    return {"status": "ok"}
