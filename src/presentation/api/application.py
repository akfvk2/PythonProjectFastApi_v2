from fastapi import FastAPI, APIRouter
from fastapi.responses import UJSONResponse
from starlette.middleware.cors import CORSMiddleware
from src.presentation.api.router import router as orders_router






def get_app() -> FastAPI:
    app = FastAPI(
        docs_url="/docs",
        openapi_url="/openapi.json",
        default_response_class=UJSONResponse,
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