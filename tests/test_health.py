from fastapi.testclient import TestClient

from server.main import app


def test_root_and_health() -> None:
    client = TestClient(app)

    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert "message" in data and data["message"]
    assert "endpoints" in data and "health" in data["endpoints"]

    h = client.get("/health")
    assert h.status_code == 200
    hdata = h.json()
    # Adjust keys if your HealthResponse differs
    assert isinstance(hdata, dict)
