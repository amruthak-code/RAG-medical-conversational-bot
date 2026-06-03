import logging
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO)
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import os

from database import init_db
from routers import upload, chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Post-Discharge Care Agent", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(chat.router)

FRONTEND_PATH = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")


@app.get("/", include_in_schema=False)
async def serve_frontend():
    return FileResponse(
        FRONTEND_PATH,
        headers={"Cache-Control": "no-store, no-cache, must-revalidate"},
    )


@app.get("/api/health")
async def health():
    from config import settings
    def mask(val: str) -> str:
        return val[:6] + "..." if val and len(val) > 6 else ("SET" if val else "NOT SET")
    return {
        "status": "ok",
        "pinecone_api_key": mask(settings.pinecone_api_key),
        "gemini_api_key": mask(settings.gemini_api_key),
        "sendgrid_api_key": mask(settings.sendgrid_api_key),
        "pinecone_index": settings.pinecone_index_name,
        "database_url": settings.database_url.split("@")[-1],  # hide credentials
    }


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"{type(exc).__name__}: {exc}"},
    )
