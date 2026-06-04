import httpx
from uuid import UUID
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential_jitter,
    retry_if_exception_type,
)
from src.application.ports.first_service_client import AbstractFirstServiceClient
from src.infrastructure.http.circuit_breaker import AsyncCircuitBreaker, CircuitBreakerOpenError


_circuit_breaker = AsyncCircuitBreaker(fail_max=5, reset_timeout=30)

class HttpxFirstServiceClient(AbstractFirstServiceClient):
    def __init__(self, client: httpx.AsyncClient):
        self._client = client

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential_jitter(initial=0.5, max=5.0, jitter=1.0),
        retry=retry_if_exception_type(httpx.HTTPError),

    )
    async def _fetch(self, order_id: UUID) -> dict:
        response = await self._client.get(f"/orders/{order_id}")
        response.raise_for_status()
        return response.json()

    async def get_order(self, order_id: UUID) -> dict:
        return await _circuit_breaker.call(self._fetch, order_id)