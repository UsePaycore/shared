from typing import Any

from .billing_declarative_base import BillingBase
from .timestamp_mixin import TimestampMixin


class BillingBaseModel(BillingBase, TimestampMixin):
    __abstract__ = True

    def to_dict(self) -> dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
