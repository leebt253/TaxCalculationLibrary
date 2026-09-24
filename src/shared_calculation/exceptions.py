"""Exceptions raised by the shared calculation library."""

from __future__ import annotations

from typing import Any, Optional


class ValidationError(ValueError):
    """Structured validation failure for metadata or an input record."""

    def __init__(
        self,
        *,
        row: Optional[int],
        field: Optional[str],
        value: Any,
        code: str,
        message: str,
    ) -> None:
        self.row = row
        self.field = field
        self.value = value
        self.code = code
        self.message = message
        super().__init__(message)
