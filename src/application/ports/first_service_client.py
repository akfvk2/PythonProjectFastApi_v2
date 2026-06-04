from abc import ABC, abstractmethod
from uuid import UUID

class AbstractFirstServiceClient(ABC):

    @abstractmethod
    async def get_order(self, order_id: UUID) -> dict:
        raise NotImplementedError