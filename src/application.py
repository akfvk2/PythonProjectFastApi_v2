from fastapi import FastAPI
from fastapi.responses import UJSONResponse
from starlette.middleware.cors import CORSMiddleware
from src.orders.router import router as orders_router


def _setup_routers(app: FastAPI) -> None:
    app.include_router(orders_router, prefix="/v1/orders", tags=["orders"])

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

    _setup_routers(app)

    return app