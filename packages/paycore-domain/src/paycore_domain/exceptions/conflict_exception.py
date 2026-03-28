from typing import Any, Dict, Optional

from .domain_exception import DomainException


class ConflictException(DomainException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message, "CONFLICT", details)
