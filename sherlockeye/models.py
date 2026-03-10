from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, TypedDict


SearchType = Literal["email", "domain", "ip", "username", "phone", "cpf", "cnpj", "name"]


class BalanceData(TypedDict):
    tokens: float


class BalanceResponse(TypedDict):
    success: Literal[True]
    data: BalanceData


class ErrorDetails(TypedDict, total=False):
    # Open structure; API may return arbitrary keys.
    # Kept as Dict[str, Any] in ErrorResponse below.
    pass


class ErrorResponse(TypedDict):
    success: Literal[False]
    errorCode: str
    message: str
    details: Dict[str, Any]


class CreateSearchRequest(TypedDict, total=False):
    type: SearchType
    value: str
    additional_modules: List[str]


class CreateSearchData(TypedDict):
    searchId: str
    type: SearchType
    value: str
    status: Literal["processing", "complete"]
    createdAt: str


class CreateSearchResponse(TypedDict):
    success: Literal[True]
    data: CreateSearchData


class SearchResult(TypedDict):
    id: str
    source: str
    attributes: Dict[str, str]


class CreateSyncSearchRequest(TypedDict, total=False):
    type: SearchType
    value: str
    timeoutSeconds: int
    additional_modules: List[str]
    strict_sources: List[str]
    strict_attributes: List[str]


class CreateSyncSearchData(TypedDict):
    searchId: str
    type: SearchType
    value: str
    timeoutSeconds: int
    status: Literal["partial", "complete"]
    progress: int
    results: List[SearchResult]


class CreateSyncSearchResponse(TypedDict):
    success: Literal[True]
    data: CreateSyncSearchData


class GetSearchData(TypedDict, total=False):
    # Simplified schema; API may return more fields.
    searchId: str
    type: SearchType
    value: str
    status: str
    createdAt: str
    # Results may follow the same format as SearchResult.
    results: List[SearchResult]


class GetSearchResponse(TypedDict):
    success: Literal[True]
    data: GetSearchData


class DeleteSearchData(TypedDict, total=False):
    searchId: str
    deleted: bool


class DeleteSearchResponse(TypedDict):
    success: Literal[True]
    data: DeleteSearchData


class BlockchainData(TypedDict, total=False):
    searchId: str
    txHash: str
    explorerUrl: Optional[str]


class BlockchainResponse(TypedDict):
    success: Literal[True]
    data: BlockchainData


class CreateWebhookRequest(TypedDict, total=False):
    url: str
    events: List[str]
    enabled: bool
    secret: Optional[str]


class UpdateWebhookRequest(TypedDict, total=False):
    url: str
    events: List[str]
    enabled: bool
    secret: Optional[str]


class Webhook(TypedDict, total=False):
    id: str
    url: str
    events: List[str]
    enabled: bool
    secret: Optional[str]


class WebhookResponse(TypedDict):
    success: Literal[True]
    data: Webhook


class WebhookListData(TypedDict):
    items: List[Webhook]


class WebhookListResponse(TypedDict):
    success: Literal[True]
    data: WebhookListData


class DeleteWebhookData(TypedDict, total=False):
    id: str
    deleted: bool


class DeleteWebhookResponse(TypedDict):
    success: Literal[True]
    data: DeleteWebhookData


class WebhookDeliveryAttempt(TypedDict, total=False):
    id: str
    status: str
    responseStatusCode: Optional[int]
    responseBody: Optional[str]
    createdAt: str


class WebhookDelivery(TypedDict, total=False):
    id: str
    webhookId: str
    status: str
    createdAt: str
    attempts: List[WebhookDeliveryAttempt]


class WebhookDeliveriesData(TypedDict):
    items: List[WebhookDelivery]


class WebhookDeliveriesResponse(TypedDict):
    success: Literal[True]
    data: WebhookDeliveriesData


class WebhookRetryData(TypedDict, total=False):
    deliveryId: str
    status: str


class WebhookRetryResponse(TypedDict):
    success: Literal[True]
    data: WebhookRetryData

