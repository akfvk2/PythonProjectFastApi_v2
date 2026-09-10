class RetryException(Exception):
    def __init__(self, message: str = "Temporary infrastructure error"):
        super().__init__(message)