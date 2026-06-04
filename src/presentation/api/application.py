import httpx
from fastapi import FastAPI, APIRouter
from fastapi.responses import UJSONResponse
from starlette.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.presentation.api.router import router as orders_router
from src.infrastructure.http.first_service_client import HttpxFirstServiceClient
from src.infrastructure.config import settings
from redis.asyncio import Redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    app.state.redis = redis

    async with httpx.AsyncClient(base_url=settings.first_service_url) as client:
        app.state.first_service_client = HttpxFirstServiceClient(client)
        yield

    await redis.aclose()


def get_app() -> FastAPI:
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

    api_v1_router = APIRouter(prefix="/v1")
    api_v1_router.include_router(orders_router, prefix="/orders", tags=["orders"])
    app.include_router(api_v1_router)

    return app