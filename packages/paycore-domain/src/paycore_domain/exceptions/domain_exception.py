from typing import Any, Dict, Optional


class DomainException(Exception):
    def __init__(
        self, message: str, code: Optional[str] = None, details: Optional[Dict[str, Any]] = None
    ) -> None:
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": self.code,
            "message": self.message,
            "details": self.details,
        }
