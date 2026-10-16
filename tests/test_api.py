import asyncio
import json
from io import BytesIO

import pytest
from fastapi import UploadFile

from app.config import settings
from app.main import health_check
from app.routes.receipts import analyze


def test_health_works_without_openai_configuration(monkeypatch):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "")
    monkeypatch.setattr(settings, "OPENAI_RECEIPT_MODEL", "")

    assert asyncio.run(health_check()) == {"status": "ok"}


@pytest.mark.parametrize(
    ("api_key", "model"),
    [("", "gpt-4o-mini"), ("configured-for-test", "")],
)
def test_analyze_returns_service_unavailable_without_openai_configuration(
    monkeypatch, api_key, model
):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", api_key)
    monkeypatch.setattr(settings, "OPENAI_RECEIPT_MODEL", model)

    image = UploadFile(filename="receipt.jpg", file=BytesIO(b"not-a-real-image"))
    response = asyncio.run(analyze(request=None, image=image))
    body = json.loads(response.body)

    assert response.status_code == 503
    assert body["error"]["code"] == "SERVICE_UNAVAILABLE"
    assert body["error"]["message"] == "Fiş analiz servisi şu anda kullanılamıyor."
    assert isinstance(body["error"]["requestId"], str)
    assert body["error"]["requestId"]
