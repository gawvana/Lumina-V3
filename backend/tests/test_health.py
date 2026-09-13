import pytest

pytestmark = pytest.mark.asyncio

async def test_health_endpoint(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

async def test_ready_endpoint(client):
    response = await client.get("/ready")
    assert response.status_code == 200
    assert "status" in response.json()
