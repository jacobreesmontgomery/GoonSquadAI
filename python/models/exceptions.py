class BaseHTTPException(Exception):

    message: str = "An error occurred."
    status_code: int = 500

    def __init__(self, message: str | None = None, status_code: int | None = None):
        self.message = message or self.message
        self.status_code = status_code or self.status_code
        super().__init__(self.message)


class QueryGenerationException(BaseHTTPException):

    message: str = "An error occurred while generating the query."
    status_code: int = 500


class QueryExecutionException(BaseHTTPException):

    message: str = "An error occurred while executing the query."
    status_code: int = 500


class LowConfidenceQueryException(BaseHTTPException):

    message: str = "The confidence level of the generated query is too low."
    status_code: int = 500
