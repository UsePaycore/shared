from typing import Any, Dict, Optional

from .domain_exception import DomainException


class ValidationException(DomainException):
    def __init__(
        self, message: str, field: Optional[str] = None, details: Optional[Dict[str, Any]] = None
    ) -> None:
        details = details or {}
        if field:
            details["field"] = field
        super().__init__(message, "VALIDATION_ERROR", details)
