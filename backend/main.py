import asyncio
import logging
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
    first = asyncio.create_task(_boilerplate_refresh())        # in the background: startup does not wait
    task = asyncio.create_task(_maintenance_every(float(os.getenv("REJOIN_INTERVAL_HOURS", "6"))))
    yield
    first.cancel()
    task.cancel()


async def _boilerplate_refresh():
    from backend.services import boilerplate
    try:
        result = await asyncio.to_thread(boilerplate.refresh)
        logging.getLogger(__name__).info("boilerplate refresh: %s", result)
    except Exception:
        logging.getLogger(__name__).exception("boilerplate refresh failed")


async def _maintenance_every(hours):
    """Maintenance that needs no operator, once per 6-hour window by default: the boilerplate list
    (Phase 1), a case re-joining pass (unless REJOIN_ENABLED=0) and topic clustering; a failure is
    logged and retried next interval."""
    from backend.services import rejoin

    while True:
        await asyncio.sleep(hours * 3600)
        await _boilerplate_refresh()
        try:
            if not rejoin.enabled():
                raise LookupError("re-joining disabled")
            from backend.routers.dashboard import dashboard_rejoin
            result = await asyncio.to_thread(dashboard_rejoin)
            logging.getLogger(__name__).info("scheduled re-joining pass: %d merges", len(result.get("merges", [])))
        except LookupError:
            pass
        except Exception:
            logging.getLogger(__name__).exception("scheduled re-joining pass failed")
        try:                                       # topics carry the department each escalation is routed to
            from backend.services.clustering_service import cluster_cases
            result = await asyncio.to_thread(cluster_cases)          # re-clusters only when its own rule says so
            logging.getLogger(__name__).info("scheduled topic clustering: %s", result.get("status"))
        except Exception:
            logging.getLogger(__name__).exception("scheduled topic clustering failed")


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
