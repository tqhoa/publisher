import pytest


@pytest.mark.asyncio
async def test_health_returns_ok(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


@pytest.mark.asyncio
async def test_metrics_endpoint_returns_prometheus_text(client):
    response = await client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text
