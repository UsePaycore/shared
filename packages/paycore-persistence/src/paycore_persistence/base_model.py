from typing import Any

from .declarative_base import Base
from .timestamp_mixin import TimestampMixin


class BaseModel(Base, TimestampMixin):
    __abstract__ = True

    def to_dict(self) -> dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
