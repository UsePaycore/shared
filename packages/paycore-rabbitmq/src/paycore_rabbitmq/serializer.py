import json
from typing import Any, Dict, cast

from paycore_domain.events import DomainEvent

from .encoder import DomainEventEncoder


class DomainEventJsonSerializer:
    @staticmethod
    def serialize(event: DomainEvent) -> str:
        return json.dumps(event.to_dict(), cls=DomainEventEncoder)

    @staticmethod
    def deserialize(data: str) -> Dict[str, Any]:
        return cast(Dict[str, Any], json.loads(data))
