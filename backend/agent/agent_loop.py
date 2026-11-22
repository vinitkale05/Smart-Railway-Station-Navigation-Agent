import time
from typing import Dict, Any, List
from backend.models.schemas import MessageResponse, Session
from backend.models.database import db_get_session, db_save_session, db_log_turn
from backend.agent.guardrails import sanitize_user_input, check_hallucination, enforce_turn_guardrails
from backend.agent.fallback_engine import run_agentic_reasoning
from backend.agent.gemini_client import run_gemini_agent_turn
from backend.models.schemas import RouteResult
from backend.config import settings

def run_agent_loop(session_id: str, user_message: str) -> MessageResponse:
    """
    Main orchestration loop for passenger queries.
    1. Sanitizes user input (redacts PNR/personal tokens).
    2. Loads active session context (current position, train, accessibility prefs).
    3. Invokes Gemini LLM with function calling if configured; falls back cleanly to deterministic agent loop.
    4. Runs guardrails: hallucination prevention, call limits.
    5. Saves session state and logs turn with latency.
    """
    start_time = time.time()
    sanitized_input = sanitize_user_input(user_message)
    
    # Retrieve session from DB
    session_data = db_get_session(session_id)
    if not session_data:
        session_data = {
            "id": session_id,
            "station_id": "pune_junction",
            "train_no": None,
            "accessibility_prefs": False,
            "current_node_id": "gate_1_main",
            "destination_node_id": None,
            "active_route": None,
            "current_step_index": 0
        }

    # Attempt Gemini Agent Turn if configured
    gemini_result = None
    if settings.GEMINI_API_KEY:
        try:
            gemini_result = run_gemini_agent_turn(sanitized_input, session_data)
        except Exception:
            gemini_result = None

    if gemini_result and gemini_result.get("text"):
        # Extract structured route from Gemini tool results if find_route was called
        route_obj = None
        train_obj = None
        for tc in gemini_result.get("tool_calls", []):
            if tc.get("tool") == "find_route" and "result" in tc:
                r_dict = tc["result"]
                if isinstance(r_dict, dict) and "nodes" in r_dict:
                    route_obj = RouteResult(**r_dict)
            elif tc.get("tool") == "get_train_info" and "result" in tc:
                train_obj = tc["result"]

        response = MessageResponse(
            text=gemini_result["text"],
            tool_calls=gemini_result.get("tool_calls", []),
            route=route_obj,
            train_info=train_obj
        )
    else:
        # Fallback to local intelligent agentic engine
        response = run_agentic_reasoning(sanitized_input, session_data)

    # Enforce turn tool limits
    if not enforce_turn_guardrails(len(response.tool_calls), settings.MAX_TOOL_CALLS_PER_TURN):
        response.tool_calls = response.tool_calls[:settings.MAX_TOOL_CALLS_PER_TURN]

    # Verify hallucination guardrail
    is_grounded = check_hallucination(response.text, response.tool_calls)
    if not is_grounded:
        response.text += "\n\n*(Note: For real-time updates, please verify platform displays or check with station inquiry.)*"

    # If a new route was computed, update the session
    if response.route:
        session_data["active_route"] = response.route.model_dump()
        session_data["destination_node_id"] = response.route.to_node
        session_data["current_step_index"] = 0
        
    if response.train_info:
        session_data["train_no"] = response.train_info.get("train_no")

    db_save_session(session_data)

    latency_ms = int((time.time() - start_time) * 1000)
    db_log_turn(
        session_id=session_id,
        role="user",
        content=sanitized_input,
        tool_calls=None,
        latency_ms=0
    )
    db_log_turn(
        session_id=session_id,
        role="assistant",
        content=response.text,
        tool_calls=response.tool_calls,
        latency_ms=latency_ms
    )

    return response
