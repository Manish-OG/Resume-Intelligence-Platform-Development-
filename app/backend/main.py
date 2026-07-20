from fastapi import FastAPI

from app.backend.api.routes import router
from src.database.db import init_db
from src.utils.logging_config import configure_logging

configure_logging()
init_db()

app = FastAPI(title="Resume Intelligence Platform API")
app.include_router(router)


@app.get("/health")
def health_check():
    return {"status": "ok"}