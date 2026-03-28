from typing import Any, Dict, Optional

from .domain_exception import DomainException


class BusinessRuleException(DomainException):
    def __init__(
        self, rule: str, message: Optional[str] = None, details: Optional[Dict[str, Any]] = None
    ) -> None:
        details = details or {}
        details["rule"] = rule
        super().__init__(message or rule, "BUSINESS_RULE_VIOLATION", details)
