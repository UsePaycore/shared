from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict
from uuid import UUID, uuid4


@dataclass(frozen=True, kw_only=True)
class DomainEvent(ABC):
    aggregate_id: UUID
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=datetime.utcnow)

    @staticmethod
    @abstractmethod
    def event_name() -> str:
        pass

    @abstractmethod
    def to_primitives(self) -> Dict[str, Any]:
        pass

    @classmethod
    @abstractmethod
    def from_primitives(
        cls,
        aggregate_id: UUID,
        event_id: UUID,
        occurred_at: datetime,
        body: Dict[str, Any],
    ) -> "DomainEvent":
        pass

    @property
    def event_type(self) -> str:
        return self.__class__.__name__

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "event_name": self.event_name(),
            "aggregate_id": str(self.aggregate_id),
            "occurred_at": self.occurred_at.isoformat(),
            "body": self.to_primitives(),
        }
