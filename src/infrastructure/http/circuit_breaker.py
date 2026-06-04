import time
from enum import Enum

class CBState(Enum):
    CLOSED = "closed"      # всё ок, запросы проходят
    OPEN = "open"          # слишком много ошибок, fast-fail
    HALF_OPEN = "half_open"  # пробный запрос после таймаута

class CircuitBreakerOpenError(Exception):
    pass

class AsyncCircuitBreaker:
    def __init__(self, fail_max: int = 5, reset_timeout: int = 30):
        self.fail_max = fail_max
        self.reset_timeout = reset_timeout
        self._failures = 0
        self._state = CBState.CLOSED
        self._opened_at: float | None = None

    @property
    def state(self) -> CBState:
        if self._state == CBState.OPEN:
            if time.monotonic() - self._opened_at >= self.reset_timeout:
                return CBState.HALF_OPEN
        return self._state

    async def call(self, func, *args, **kwargs):
        state = self.state
        if state == CBState.OPEN:
            raise CircuitBreakerOpenError("Circuit breaker is OPEN — fast fail")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except CircuitBreakerOpenError:
            raise
        except Exception:
            self._on_failure()
            raise

    def _on_success(self):
        self._failures = 0
        self._state = CBState.CLOSED

    def _on_failure(self):
        self._failures += 1
        if self._failures >= self.fail_max:
            self._state = CBState.OPEN
            self._opened_at = time.monotonic()