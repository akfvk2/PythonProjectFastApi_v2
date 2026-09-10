from fastapi import FastAPI
from fastapi.responses import UJSONResponse
from starlette.middleware.cors import CORSMiddleware
from src.orders.router import router as orders_router
from contextlib import asynccontextmanager
import asyncio
import contextlib
from src.students.consumer import run_student_events_consumer
import logging

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(run_student_events_consumer())
    yield
    task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await task

def _setup_routers(app: FastAPI) -> None:
    app.include_router(orders_router, prefix="/v1/orders", tags=["orders"])

def get_app() -> FastAPI:
    logging.basicConfig(level=logging.INFO)
    app = FastAPI(
        docs_url="/docs",
        openapi_url="/openapi.json",
        default_response_class=UJSONResponse,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    _setup_routers(app)

    return app