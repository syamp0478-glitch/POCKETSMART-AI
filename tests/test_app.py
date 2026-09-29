import pytest
from fastapi.testclient import TestClient
from app.config import settings
from app.main import app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "database_path", str(tmp_path / "test.db"))
    with TestClient(app) as test_client:
        yield test_client


def create_account(client):
    response = client.post("/register", json={"name": "Taylor Smart", "email": "taylor@example.com", "password": "safe-password-123"})
    assert response.status_code == 201
    return response.json()["access_token"]


def test_health_and_frontend(client):
    assert client.get("/health").json()["status"] == "ok"
    page = client.get("/")
    assert page.status_code == 200
    assert "PocketSmart" in page.text


def test_auth_and_home_recommendation_history(client):
    token = create_account(client)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/generate-home", headers=headers, json={
        "budget": 30000, "currency": "INR", "rooms": ["Living room", "Bedroom"], "style": "Modern", "priorities": "storage"
    })
    assert response.status_code == 200, response.text
    plan = response.json()
    assert plan["estimated_total"] <= plan["budget"]
    assert plan["recommendations"]
    assert client.get("/history", headers=headers).json()[0]["planner"] == "home"
    assert client.post("/generate-home", json={"budget": 20, "rooms": ["Bedroom"]}).status_code == 401


def test_party_validation_and_jewelry_image(client):
    token = create_account(client)
    headers = {"Authorization": f"Bearer {token}"}
    party = client.post("/generate-party", headers=headers, json={
        "budget": 10000, "event_type": "Birthday", "guests": 12, "venue": "At home", "city": "Pune"
    })
    assert party.status_code == 200, party.text
    assert party.json()["planner"] == "party"
    jewelry = client.post("/generate-jewelry", headers=headers, data={
        "budget": "5000", "occasion": "Wedding", "style": "Classic", "outfit_colors": "blue"
    }, files={"image": ("outfit.png", b"not-a-real-image", "image/png")})
    # The optional image is safely transmitted to the configured AI layer; with no key the deterministic plan works.
    assert jewelry.status_code == 200, jewelry.text
    assert jewelry.json()["planner"] == "jewelry"


def test_duplicate_account_and_bad_login(client):
    create_account(client)
    assert client.post("/register", json={"name": "Taylor Smart", "email": "taylor@example.com", "password": "safe-password-123"}).status_code == 409
    assert client.post("/login", json={"email": "taylor@example.com", "password": "wrong-password"}).status_code == 401
