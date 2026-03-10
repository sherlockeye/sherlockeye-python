from __future__ import annotations

from typing import Any, Dict, Optional


class SherlockeyeError(Exception):
    """Base error for all Sherlockeye client exceptions."""

    def __init__(
        self,
        message: str,
        *,
        status_code: Optional[int] = None,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}


class SherlockeyeAuthError(SherlockeyeError):
    """Authentication/authorization errors (401, 403)."""


class SherlockeyeRateLimitError(SherlockeyeError):
    """Rate-limit or credits related errors (429)."""


class SherlockeyeValidationError(SherlockeyeError):
    """Input validation errors (400, 422)."""


class SherlockeyeApiAccessError(SherlockeyeError):
    """API is not enabled for the current user/plan."""


class SherlockeyeServerError(SherlockeyeError):
    """5xx or unexpected API responses."""

