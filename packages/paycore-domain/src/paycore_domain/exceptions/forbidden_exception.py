from typing import Optional

from .domain_exception import DomainException


class ForbiddenException(DomainException):
    def __init__(self, message: str = "Forbidden", permission: Optional[str] = None) -> None:
        details = {"permission": permission} if permission else {}
        super().__init__(message, "FORBIDDEN", details)
