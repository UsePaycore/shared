from typing import Any, Optional

from .domain_exception import DomainException


class NotFoundException(DomainException):
    def __init__(self, entity_type: str, entity_id: Optional[Any] = None) -> None:
        if entity_id is not None:
            message = f"{entity_type} with id '{entity_id}' not found"
            details = {"entity_type": entity_type, "entity_id": str(entity_id)}
        else:
            message = entity_type
            details = {}
        super().__init__(message, "NOT_FOUND", details)
