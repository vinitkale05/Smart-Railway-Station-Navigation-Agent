import pytest
from starlette.testclient import TestClient
from backend.main import app
from backend.data.seed_data import seed_database

@pytest.fixture(autouse=True)
def setup():
    seed_database()

client = TestClient(app)

def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_list_stations():
    res = client.get("/api/stations")
    assert res.status_code == 200
    stations = res.json()
    assert len(stations) >= 1
    assert stations[0]["id"] == "pune_junction"

def test_get_station_graph():
    res = client.get("/api/stations/pune_junction/graph")
    assert res.status_code == 200
    data = res.json()
    assert "nodes" in data
    assert "edges" in data
    assert len(data["nodes"]) >= 30

def test_create_session_and_message():
    # 1. Create session
    s_res = client.post("/api/sessions", json={"train_no": "12951", "accessibility_prefs": True})
    assert s_res.status_code == 201
    sess_id = s_res.json()["id"]

    # 2. Send message
    m_res = client.post(f"/api/sessions/{sess_id}/messages", json={"message": "Where is my train 12951?"})
    assert m_res.status_code == 200
    data = m_res.json()
    assert "Platform 4" in data["text"]
    assert data["route"] is not None

def test_admin_flow():
    # 1. Login
    login_res = client.post("/api/admin/login", json={"username": "station_admin", "password": "admin123"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Change Platform
    change_res = client.post("/api/admin/platform-changes", headers=headers, json={
        "train_no": "12124",
        "new_platform": "Platform 3",
        "delay_minutes": 10,
        "reason": "Signal clearance"
    })
    assert change_res.status_code == 200
    assert change_res.json()["status"] == "success"

    # 3. Check train updated
    t_res = client.get("/api/trains/12124")
    assert t_res.status_code == 200
    assert t_res.json()["platform"] == "Platform 3"
    assert t_res.json()["status"] == "Platform Changed"
