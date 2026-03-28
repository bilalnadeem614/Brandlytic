import pytest
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ── Health ────────────────────────────────────────────────────────────────────

def test_health(client):
    res = client.get("/api/v1/health")
    assert res.status_code == 200
    assert res.get_json()["status"] == "ok"


# ── /generate ─────────────────────────────────────────────────────────────────

def test_generate_missing_input(client):
    res = client.post("/api/v1/brand/generate", json={})
    assert res.status_code == 400
    assert res.get_json()["success"] is False


def test_generate_empty_input(client):
    res = client.post("/api/v1/brand/generate", json={"input": "   "})
    assert res.status_code == 400


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


# ── /refine ───────────────────────────────────────────────────────────────────

def test_refine_missing_field(client):
    res = client.post("/api/v1/brand/refine", json={
        "input": "A coffee shop in Karachi",
        "platform": "general",
        "rejected_value": "CafeKhi",
        "rejection_reason": "Too generic"
    })
    assert res.status_code == 400
    assert res.get_json()["success"] is False


def test_refine_invalid_field(client):
    res = client.post("/api/v1/brand/refine", json={
        "input": "A coffee shop in Karachi",
        "platform": "general",
        "field": "nonexistent_field",
        "rejected_value": "something",
        "rejection_reason": "doesn't fit"
    })
    assert res.status_code == 400
    assert "field" in res.get_json()["error"].lower()


def test_refine_missing_rejection_reason(client):
    res = client.post("/api/v1/brand/refine", json={
        "input": "A coffee shop in Karachi",
        "platform": "general",
        "field": "tagline",
        "rejected_value": "Brewed for you",
    })
    assert res.status_code == 400


def test_refine_invalid_platform(client):
    res = client.post("/api/v1/brand/refine", json={
        "input": "A coffee shop in Karachi",
        "platform": "snapchat",
        "field": "tagline",
        "rejected_value": "Brewed for you",
        "rejection_reason": "Too bland"
    })
    assert res.status_code == 400
    assert "platform" in res.get_json()["error"].lower()


def test_refine_no_body(client):
    res = client.post("/api/v1/brand/refine")
    assert res.status_code == 400
