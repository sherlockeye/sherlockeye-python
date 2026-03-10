from __future__ import annotations

import time
from typing import Any, Dict, Optional, TypeVar

import httpx

from .exceptions import (
    SherlockeyeApiAccessError,
    SherlockeyeAuthError,
    SherlockeyeError,
    SherlockeyeRateLimitError,
    SherlockeyeServerError,
    SherlockeyeValidationError,
)
from .models import (
    BalanceResponse,
    BlockchainResponse,
    CreateSearchRequest,
    CreateSearchResponse,
    CreateSyncSearchRequest,
    CreateSyncSearchResponse,
    DeleteSearchResponse,
    GetSearchResponse,
    SearchResult,
    WebhookDeliveriesResponse,
    WebhookListResponse,
    WebhookResponse,
    WebhookRetryResponse,
)


T = TypeVar("T", bound=Dict[str, Any])


class SherlockeyeClient:
    """
    Synchronous client for the Sherlockeye API.

    Usage example:

        from sherlockeye import SherlockeyeClient

        client = SherlockeyeClient(api_key="your_api_key")
        balance = client.get_balance()
        print(balance["data"]["tokens"])
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = "https://api.sherlockeye.io",
        timeout: float = 30.0,
        max_retries: int = 3,
    ) -> None:
        if not api_key:
            raise ValueError("api_key must not be empty.")

        self._client = httpx.Client(
            base_url=base_url.rstrip("/"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            timeout=timeout,
        )
        self._max_retries = max_retries

    def close(self) -> None:
        """Close underlying HTTP connections."""
        self._client.close()

    def __enter__(self) -> "SherlockeyeClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    # ------------------------------------------------------------
    # Public API methods
    # ------------------------------------------------------------

    def get_balance(self) -> BalanceResponse:
        """GET /v1/balance — token balance for the authenticated user."""
        return self._request("GET", "/v1/balance")

    def create_search(self, payload: CreateSearchRequest) -> CreateSearchResponse:
        """POST /v1/searches — create an asynchronous OSINT search."""
        return self._request("POST", "/v1/searches", json=payload)

    def get_search(self, search_id: str) -> GetSearchResponse:
        """GET /v1/searches/{searchId} — search details and results."""
        if not search_id:
            raise ValueError("search_id must not be empty.")
        path = f"/v1/searches/{search_id}"
        return self._request("GET", path)

    def delete_search(self, search_id: str) -> DeleteSearchResponse:
        """DELETE /v1/searches/{searchId} — delete a search and its identifier."""
        if not search_id:
            raise ValueError("search_id must not be empty.")
        path = f"/v1/searches/{search_id}"
        return self._request("DELETE", path)

    def create_sync_search(
        self, payload: CreateSyncSearchRequest
    ) -> CreateSyncSearchResponse:
        """POST /v1/searches/sync — synchronous OSINT search with timeout."""
        return self._request("POST", "/v1/searches/sync", json=payload)

    def register_search_on_blockchain(self, search_id: str) -> BlockchainResponse:
        """
        POST /v1/blockchain/searches/{searchId} or equivalent route.

        The official documentation should be consulted to confirm the exact path.
        """
        if not search_id:
            raise ValueError("search_id must not be empty.")
        path = f"/v1/blockchain/searches/{search_id}"
        return self._request("POST", path)

    # ----------------- Webhooks -----------------

    def create_webhook(self, payload: Dict[str, Any]) -> WebhookResponse:
        """POST /v1/webhooks — create a new webhook."""
        return self._request("POST", "/v1/webhooks", json=payload)

    def list_webhooks(self) -> WebhookListResponse:
        """GET /v1/webhooks — list all webhooks for the authenticated user."""
        return self._request("GET", "/v1/webhooks")

    def get_webhook(self, webhook_id: str) -> WebhookResponse:
        """GET /v1/webhooks/{webhookId} — webhook details."""
        if not webhook_id:
            raise ValueError("webhook_id must not be empty.")
        path = f"/v1/webhooks/{webhook_id}"
        return self._request("GET", path)

    def update_webhook(self, webhook_id: str, payload: Dict[str, Any]) -> WebhookResponse:
        """PATCH /v1/webhooks/{webhookId} — update a webhook."""
        if not webhook_id:
            raise ValueError("webhook_id must not be empty.")
        path = f"/v1/webhooks/{webhook_id}"
        return self._request("PATCH", path, json=payload)

    def delete_webhook(self, webhook_id: str) -> Dict[str, Any]:
        """DELETE /v1/webhooks/{webhookId} — delete a webhook."""
        if not webhook_id:
            raise ValueError("webhook_id must not be empty.")
        path = f"/v1/webhooks/{webhook_id}"
        return self._request("DELETE", path)

    def get_webhook_deliveries(self, webhook_id: str) -> WebhookDeliveriesResponse:
        """GET /v1/webhooks/{webhookId}/deliveries — delivery history."""
        if not webhook_id:
            raise ValueError("webhook_id must not be empty.")
        path = f"/v1/webhooks/{webhook_id}/deliveries"
        return self._request("GET", path)

    def retry_webhook_delivery(
        self, webhook_id: str, delivery_id: str
    ) -> WebhookRetryResponse:
        """POST /v1/webhooks/{webhookId}/deliveries/{deliveryId}/retry — retry a delivery."""
        if not webhook_id:
            raise ValueError("webhook_id must not be empty.")
        if not delivery_id:
            raise ValueError("delivery_id must not be empty.")
        path = f"/v1/webhooks/{webhook_id}/deliveries/{delivery_id}/retry"
        return self._request("POST", path)

    # ------------------------------------------------------------
    # Request core and error handling
    # ------------------------------------------------------------

    def _request(self, method: str, path: str, *, json: Optional[Dict[str, Any]] = None) -> T:
        url = path if path.startswith("/") else f"/{path}"

        last_exc: Optional[Exception] = None
        for attempt in range(self._max_retries + 1):
            try:
                response = self._client.request(method, url, json=json)
            except httpx.HTTPError as exc:  # network error, timeout, etc.
                last_exc = exc
                # Only retry while we still have attempts.
                if attempt < self._max_retries:
                    time.sleep(0.5 * (attempt + 1))
                    continue
                raise SherlockeyeServerError(
                    f"Network error while calling Sherlockeye API: {exc}"
                ) from exc

            if 200 <= response.status_code < 300:
                try:
                    data = response.json()
                except ValueError as exc:
                    raise SherlockeyeServerError(
                        f"Invalid JSON response from Sherlockeye API (status {response.status_code})."
                    ) from exc
                return data  # type: ignore[return-value]

            # Error handling based on ErrorResponse contract.
            try:
                payload = response.json()
            except ValueError:
                raise SherlockeyeServerError(
                    f"HTTP {response.status_code} from Sherlockeye API with non-JSON body."
                )

            message = payload.get("message") or "Error while calling Sherlockeye API."
            error_code = payload.get("errorCode")
            details = payload.get("details") or {}

            # Map status code + errorCode to specific exceptions.
            if response.status_code in (401, 403):
                raise SherlockeyeAuthError(
                    message,
                    status_code=response.status_code,
                    error_code=error_code,
                    details=details,
                )

            if response.status_code in (400, 422):
                if error_code in (
                    "INVALID_ADDITIONAL_MODULES",
                    "INVALID_TIMEOUT",
                    "INVALID_VALUE_FORMAT",
                    "INVALID_STRICT_SOURCES",
                    "INVALID_STRICT_ATTRIBUTES",
                ):
                    raise SherlockeyeValidationError(
                        message,
                        status_code=response.status_code,
                        error_code=error_code,
                        details=details,
                    )
                raise SherlockeyeValidationError(
                    message,
                    status_code=response.status_code,
                    error_code=error_code,
                    details=details,
                )

            if response.status_code == 403 and error_code == "API_ACCESS_NOT_ALLOWED":
                raise SherlockeyeApiAccessError(
                    message,
                    status_code=response.status_code,
                    error_code=error_code,
                    details=details,
                )

            if response.status_code == 429:
                # Rate limit / credits.
                if attempt < self._max_retries:
                    time.sleep(1.0 * (attempt + 1))
                    continue
                raise SherlockeyeRateLimitError(
                    message,
                    status_code=response.status_code,
                    error_code=error_code,
                    details=details,
                )

            if 500 <= response.status_code <= 599:
                if attempt < self._max_retries:
                    time.sleep(0.5 * (attempt + 1))
                    continue
                raise SherlockeyeServerError(
                    message,
                    status_code=response.status_code,
                    error_code=error_code,
                    details=details,
                )

            # Any other combination falls back to a generic error.
            raise SherlockeyeError(
                message,
                status_code=response.status_code,
                error_code=error_code,
                details=details,
            )

        # In theory, we should never reach this line.
        raise SherlockeyeServerError(
            "Unknown failure while calling Sherlockeye API."
        ) from last_exc

