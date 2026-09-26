class RetryException(Exception):
    def __init__(self, message: str = "Temporary infrastructure error", retry_delay: float | None = None):
        super().__init__(message)
        self.retry_delay = retry_delay