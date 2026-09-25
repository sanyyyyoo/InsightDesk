import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.auth import require_admin
from backend.chatbot.router import router as chatbot_router
from backend.routers.complaints import get_pipeline, router as complaints_router
from backend.routers.dashboard import router as dashboard_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load MiniLM, the cross-encoder and Pinecone at startup so the
    # first customer submission doesn't wait for model loading.
    get_pipeline()
    yield


app = FastAPI(
    title="InsightDesk API",
    version="1.0.0",
    lifespan=lifespan
)


# Browser frontends (e.g. React dev server on :5173) calling the API.
cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.get("/")
def home():

    return {
        "message": "InsightDesk API is running 🚀"
    }


# Customer submission (login required): POST /analyze
app.include_router(
    complaints_router
)

# Operator endpoints: admin login required once ADMIN_AUTH_REQUIRED=true
app.include_router(
    chatbot_router,
    dependencies=[Depends(require_admin)]
)

app.include_router(
    dashboard_router,
    dependencies=[Depends(require_admin)]
)
