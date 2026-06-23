class OrderNotFoundError(Exception):
    def __init__(self, order_id):
        self.order_id = order_id
        super().__init__(f"Order {order_id} not found")

class OrderAlreadyExistsError(Exception):
    def __init__(self, order_id):
        self.order_id = order_id
        super().__init__(f"Order {order_id} already exists")

class ExternalServiceError(Exception):
    def __init__(self, message: str = "First service unavailable"):
        super().__init__(message)