import pytest
from backend.tools.implementations import (
    get_train_info,
    find_route,
    find_facility,
    get_platform_status,
    get_lift_status,
    send_alert_to_user
)
from backend.data.seed_data import seed_database

@pytest.fixture(autouse=True)
def setup():
    seed_database()

def test_get_train_info():
    res = get_train_info("12951")
    assert res["found"] is True
    assert res["train_no"] == "12951"
    assert res["platform"] == "Platform 4"
    assert "Rajdhani" in res["name"]

def test_get_train_info_not_found():
    res = get_train_info("99999")
    assert res["found"] is False
    assert "error" in res

def test_find_facility_washroom():
    res = find_facility("washroom", from_node="gate_1_main")
    assert res["found"] is True
    assert res["nearest"] is not None
    assert "washroom" in res["nearest"]["facility_type"]

def test_find_facility_water():
    res = find_facility("water", from_node="gate_1_main")
    assert res["found"] is True
    assert res["nearest"]["distance_m"] > 0

def test_get_platform_status():
    res = get_platform_status("Platform 1")
    assert res["platform"] == "Platform 1"
    assert "active_trains" in res

def test_get_lift_status():
    res = get_lift_status("lift_l1_p1")
    assert res["is_lift"] is True
    assert res["is_operational"] is True

def test_send_alert():
    res = send_alert_to_user("sess_123", "Platform changed")
    assert res["delivered"] is True
