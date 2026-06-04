import pytest
import httpx
import respx
from uuid import uuid4
from src.infrastructure.http.first_service_client import HttpxFirstServiceClient
from src.infrastructure.http.circuit_breaker import AsyncCircuitBreaker


@pytest.fixture
def circuit_breaker():
    return AsyncCircuitBreaker(fail_max=5, reset_timeout=30)


@pytest.fixture
def base_url():
    return "http://test-service"


@respx.mock
async def test_get_order_success(base_url):
    order_id = uuid4()
    respx.get(f"{base_url}/orders/{order_id}").mock(
        return_value=httpx.Response(200, json={"title": "Test", "price": 50.0})
    )

    async with httpx.AsyncClient(base_url=base_url) as client:
        svc = HttpxFirstServiceClient(client)
        result = await svc.get_order(order_id)

    assert result["title"] == "Test"
    assert result["price"] == 50.0


@respx.mock
async def test_get_order_raises_on_500(base_url):
    order_id = uuid4()
    respx.get(f"{base_url}/orders/{order_id}").mock(
        return_value=httpx.Response(500)
    )

    async with httpx.AsyncClient(base_url=base_url) as client:
        svc = HttpxFirstServiceClient(client)
        with pytest.raises(Exception):
            await svc.get_order(order_id)