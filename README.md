## sherlockeye: The official Python library for Sherlockeye

Sherlockeye is a reverse search engine for investigations, fraud prevention, threat intelligence, and broader digital risk analysis.

This library lets you integrate Sherlockeye’s multi-source reverse search capabilities into your own Python applications — run OSINT searches (email, phone, username, domain, IP and more).

### Get your API KEY
https://app.sherlockeye.io/api

Full API documentation: https://docs.sherlockeye.io

### Quick start

```python
from sherlockeye import SherlockeyeClient

client = SherlockeyeClient(api_key="YOUR_API_KEY")

# Check your token balance
balance = client.get_balance()
print(balance["data"]["tokens"])

# Run a synchronous search (waits for results up to timeoutSeconds)
sync_result = client.create_sync_search(
    {
        "type": "email",
        "value": "someone@example.com",
        "timeoutSeconds": 60,
    }
)
print(sync_result["data"]["status"], sync_result["data"]["results"])
```

```python
import time
from sherlockeye import SherlockeyeClient

client = SherlockeyeClient(api_key="YOUR_API_KEY")

# Run an asynchronous search (fire-and-forget style, then poll)
search = client.create_search(
    {
        "type": "email",
        "value": "someone@example.com",
    }
)

search_id = search["data"]["searchId"]
status = search["data"]["status"]  # usually "processing"
print("Created search:", search_id, status)

# Poll until the search is complete (or a max number of attempts)
max_attempts = 10
attempt = 0

while status != "complete" and attempt < max_attempts:
    attempt += 1
    search_details = client.get_search(search_id)
    status = search_details["data"]["status"]
    print(f"[attempt {attempt}] status:", status)
    if status != "complete":
        time.sleep(5)  # wait 5 seconds before polling again

results = search_details["data"].get("results", [])
print("Final status:", status)
print("Results:", results)
```

### Installation

```bash
pip install sherlockeye
```

For local development in this repository:

```bash
pip install -e .
```

### Basic usage

```python
from sherlockeye import SherlockeyeClient

client = SherlockeyeClient(api_key="YOUR_API_KEY")

# Token balance
balance = client.get_balance()
print(balance["data"]["tokens"])

# Synchronous search
sync_result = client.create_sync_search(
    {
        "type": "ip",
        "value": "1.1.1.1",
        "timeoutSeconds": 60,  # Maximum time (in seconds) to wait for results
    }
)

status = sync_result["data"]["status"]
results = sync_result["data"]["results"]
print(status, results)

if status == "processing":
    search_id = sync_result["data"]["searchId"]
    print(
        "Warning: search is still processing. "
        "More results may become available over time. "
        f"You can poll its status and results later using get_search('{search_id}') "
    )

# Asynchronous search
search = client.create_search(
    {
        "type": "email",
        "value": "someone@example.com",
    }
)
print(search["data"]["searchId"])
```

### Webhooks

```python
# Create webhook
webhook = client.create_webhook(
    {
        "url": "https://YOUR_DOMAIN/webhooks/sherlockeye",
        "events": ["search.completed"],
        "enabled": True,
    }
)

# List webhooks
all_webhooks = client.list_webhooks()

# Delivery history
deliveries = client.get_webhook_deliveries(webhook["data"]["id"])
```

### Error handling

All API failures raise subclasses of `SherlockeyeError`:

```python
from sherlockeye import (
    SherlockeyeClient,
    SherlockeyeError,
    SherlockeyeAuthError,
    SherlockeyeRateLimitError,
    SherlockeyeValidationError,
)

client = SherlockeyeClient(api_key="YOUR_API_KEY")

try:
    balance = client.get_balance()
except SherlockeyeAuthError:
    print("Invalid API key or not allowed.")
except SherlockeyeRateLimitError:
    print("Rate limit or credits exceeded.")
except SherlockeyeValidationError as exc:
    print("Validation error:", exc)
except SherlockeyeError as exc:
    print("Generic Sherlockeye API error:", exc)
```
