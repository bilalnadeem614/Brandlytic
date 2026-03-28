import pytest
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health(client):
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    assert res.get_json()["status"] == "ok"


def test_generate_missing_input(client):
    res = client.post("/api/v1/brand/generate", json={})
    assert res.status_code == 400
    assert res.get_json()["success"] is False


def test_generate_invalid_platform(client):
    res = client.post("/api/v1/brand/generate", json={
        "input": "A coffee shop in Karachi",
        "platform": "tiktok"
    })
    assert res.status_code == 400
    assert "platform" in res.get_json()["error"].lower()


def test_generate_no_body(client):
    res = client.post("/api/v1/brand/generate")
    assert res.status_code == 400
