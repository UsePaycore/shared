import json
from datetime import datetime
from typing import Any
from uuid import UUID


class DomainEventEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        if hasattr(obj, "value"):
            return obj.value
        return super().default(obj)
