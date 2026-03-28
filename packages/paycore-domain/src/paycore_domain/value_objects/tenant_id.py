from dataclasses import dataclass
from uuid import uuid4

from .entity_id import EntityId


@dataclass(frozen=True)
class TenantId(EntityId):
    @classmethod
    def generate(cls) -> "TenantId":
        return cls(value=uuid4())
