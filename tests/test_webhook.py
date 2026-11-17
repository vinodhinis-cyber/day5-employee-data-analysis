import hashlib
import hmac

from fastapi.testclient import TestClient

import src.webhook_api as webhook_api


def test_valid_webhook(monkeypatch):
    monkeypatch.setattr(webhook_api, "WEBHOOK_SECRET", "test-secret")

    client = TestClient(webhook_api.app)

    payload = b'{"event": "customer.created", "customer_id": 101}'

    signature = hmac.new(b"test-secret", payload, hashlib.sha256).hexdigest()

    response = client.post(
        "/webhooks/customer-events", content=payload, headers={"X-Signature": signature}
    )

    assert response.status_code == 200
    assert response.json() == {"status": "accepted"}


def test_tampered_webhook(monkeypatch):
    monkeypatch.setattr(webhook_api, "WEBHOOK_SECRET", "test-secret")

    client = TestClient(webhook_api.app)

    response = client.post(
        "/webhooks/customer-events",
        content=b'{"event": "customer.created", "customer_id": 999}',
        headers={"X-Signature": "wrong-signature"},
    )

    assert response.status_code == 401


def test_missing_webhook_signature(monkeypatch):
    monkeypatch.setattr(webhook_api, "WEBHOOK_SECRET", "test-secret")

    client = TestClient(webhook_api.app)

    response = client.post(
        "/webhooks/customer-events", content=b'{"event": "customer.created"}'
    )

    assert response.status_code == 401
