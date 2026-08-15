from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.sessions import router as sessions_router
from config import CORS_ORIGINS

app = FastAPI(title="InHand", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS if CORS_ORIGINS != ["*"] else ["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sessions_router)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "name": "InHand",
        "health": "/health",
        "docs": "/docs",
        "sessions": "POST /api/sessions",
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
