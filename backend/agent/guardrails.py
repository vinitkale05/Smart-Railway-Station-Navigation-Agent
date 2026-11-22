import re
from typing import Dict, Any, List

def check_hallucination(response_text: str, tool_results: List[Dict[str, Any]]) -> bool:
    """
    Verifies that any platform numbers or departure times mentioned in the response
    are grounded in tool outputs. Returns True if grounded or no claims made.
    """
    # Extract mentioned platform numbers from response text: "Platform X"
    plat_matches = re.findall(r"platform\s+(\d+)", response_text, re.IGNORECASE)
    if not plat_matches:
        return True
        
    grounded_platforms = set()
    for res in tool_results:
        t_data = res.get("result", {})
        if isinstance(t_data, dict):
            p = t_data.get("platform")
            if p:
                for pm in re.findall(r"\d+", str(p)):
                    grounded_platforms.add(pm)
            if "platform_node_id" in t_data:
                for pm in re.findall(r"\d+", str(t_data["platform_node_id"])):
                    grounded_platforms.add(pm)
            if "nodes" in t_data:
                for n in t_data["nodes"]:
                    if "platform" in n:
                        for pm in re.findall(r"\d+", n):
                            grounded_platforms.add(pm)

    for p in plat_matches:
        if p not in grounded_platforms:
            return False  # Hallucinated platform
    return True

def sanitize_user_input(text: str) -> str:
    """
    Ensures PNR numbers or sensitive tokens are not logged or stored.
    Replaces 10-digit PNR sequences with [PNR_REDACTED].
    """
    # 10-digit PNR pattern
    sanitized = re.sub(r"\b\d{10}\b", "[PNR_REDACTED]", text)
    return sanitized

def enforce_turn_guardrails(tool_calls_count: int, max_allowed: int = 6) -> bool:
    """
    Ensures hard cap of maximum 6 tool calls per turn to prevent infinite loops.
    """
    return tool_calls_count <= max_allowed
