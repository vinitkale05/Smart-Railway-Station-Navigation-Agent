import pytest
from backend.agent.agent_loop import run_agent_loop
from backend.agent.guardrails import check_hallucination, sanitize_user_input, enforce_turn_guardrails
from backend.data.seed_data import seed_database

@pytest.fixture(autouse=True)
def setup():
    seed_database()

def test_agent_sample_interaction():
    # Test Section 20 sample interaction
    session_id = "test_interaction_sample"
    user_query = "I have train 12951 this evening. I need step-free access to the platform, and I'm carrying heavy luggage."
    resp = run_agent_loop(session_id, user_query)
    
    assert "Platform 4" in resp.text
    assert resp.route is not None
    assert resp.route.is_accessible is True
    assert len(resp.tool_calls) >= 2
    assert any(tc["tool"] == "get_train_info" for tc in resp.tool_calls)
    assert any(tc["tool"] == "find_route" for tc in resp.tool_calls)

def test_agent_clarification_on_ambiguity():
    session_id = "test_ambig"
    resp = run_agent_loop(session_id, "Where is my train platform?")
    assert resp.needs_clarification is True
    assert "train number" in resp.text.lower() or "5-digit" in resp.text.lower()

def test_pnr_redaction():
    text = "My PNR is 1234567890 where is my coach?"
    sanitized = sanitize_user_input(text)
    assert "1234567890" not in sanitized
    assert "[PNR_REDACTED]" in sanitized

def test_hallucination_guardrail():
    # If response claims Platform 99 without tool proof
    grounded = check_hallucination("Your train is on Platform 99.", [])
    assert grounded is False
    
    grounded_true = check_hallucination("Your train is on Platform 1.", [{"result": {"platform": "Platform 1"}}])
    assert grounded_true is True

def test_turn_tool_limit():
    assert enforce_turn_guardrails(4, max_allowed=6) is True
    assert enforce_turn_guardrails(7, max_allowed=6) is False
