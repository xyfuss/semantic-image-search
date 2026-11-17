from fastapi import FastAPI

app = FastAPI(title="Semantic Image Search")


@app.get("/health")
def health():
    return {"status": "ok"}