from fastapi import FastAPI

from app.backend.api.routes import router

app = FastAPI(title="Resume Intelligence Platform API")
app.include_router(router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
