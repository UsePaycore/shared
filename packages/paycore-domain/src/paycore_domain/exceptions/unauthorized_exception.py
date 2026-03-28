from .domain_exception import DomainException


class UnauthorizedException(DomainException):
    def __init__(self, message: str = "Unauthorized") -> None:
        super().__init__(message, "UNAUTHORIZED")
