from fastapi.testclient import TestClient

from app import main

client = TestClient(main.app)


def test_health_endpoints():
    assert client.get("/api/health/live").json() == {"status": "ok"}
    assert client.get("/api/health/ready").json() == {"status": "ready"}


def test_model_allowlist_rejects_unknown_model():
    response = client.post("/api/respond", json={"api_key": "sk-test-key-that-is-long-enough", "message": "hello", "model": "unknown"})
    assert response.status_code == 400


def test_response_redacts_api_key(monkeypatch):
    async def fake_response(api_key: str, model: str, message: str):
        assert api_key == "sk-test-key-that-is-long-enough"
        return {"output": "Hello", "provider_request_id": "req-provider", "latency_ms": 42, "usage": {"input_tokens": 1, "output_tokens": 1, "total_tokens": 2}}

    monkeypatch.setattr(main, "create_response", fake_response)
    response = client.post(
        "/api/respond",
        headers={"x-forwarded-for": "test-client", "x-request-id": "req-browser"},
        json={"api_key": "sk-test-key-that-is-long-enough", "message": "hello", "model": "gpt-5-mini"},
    )
    assert response.status_code == 200
    serialized = response.text
    assert "sk-test-key-that-is-long-enough" not in serialized
    assert serialized.count("[REDACTED]") >= 2
    assert response.json()["output"] == "Hello"


def test_message_size_is_bounded():
    response = client.post("/api/respond", json={"api_key": "sk-test-key-that-is-long-enough", "message": "x" * 10_001, "model": "gpt-5-mini"})
    assert response.status_code == 422
