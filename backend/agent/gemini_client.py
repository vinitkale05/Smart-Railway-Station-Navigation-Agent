import json
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional
from backend.config import settings
from backend.tools.registry import TOOL_DEFINITIONS, execute_tool_call
from backend.agent.prompts import SYSTEM_PROMPT

GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.GEMINI_MODEL}:generateContent"

def build_gemini_tools() -> List[Dict[str, Any]]:
    """
    Transforms our tool declarations into Gemini functionDeclarations format.
    """
    declarations = []
    for t in TOOL_DEFINITIONS:
        declarations.append({
            "name": t["name"],
            "description": t["description"],
            "parameters": t["parameters"]
        })
    return [{"functionDeclarations": declarations}]

def call_gemini_api(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Executes the Gemini POST request using the user-specified headers and endpoint:
    curl "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent" \
      -H 'Content-Type: application/json' \
      -H 'X-goog-api-key: <KEY>' \
      -d '{...}'
    """
    if not settings.GEMINI_API_KEY:
        return None

    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": settings.GEMINI_API_KEY
    }
    
    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        GEMINI_API_URL,
        data=data_bytes,
        headers=headers,
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=settings.REQUEST_TIMEOUT_SECONDS) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body)
    except Exception as e:
        # If offline or network-blocked, log and return None so fallback activates cleanly
        # print(f"Gemini API call failed: {e}")
        return None

def run_gemini_agent_turn(user_query: str, session: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Runs an interactive turn with Gemini Flash using function calling.
    Returns None if the API cannot be reached, triggering the fallback engine.
    """
    tools = build_gemini_tools()
    
    contents = [
        {
            "role": "user",
            "parts": [
                {"text": f"Context: Passenger is at station 'pune_junction', current location '{session.get('current_node_id', 'gate_1_main')}', accessibility required: {session.get('accessibility_prefs', False)}, train: {session.get('train_no')}.\n\nPassenger query: {user_query}"}
            ]
        }
    ]

    payload = {
        "systemInstruction": {
            "parts": [{"text": SYSTEM_PROMPT}]
        },
        "contents": contents,
        "tools": tools,
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 800
        }
    }

    first_res = call_gemini_api(payload)
    if not first_res or "candidates" not in first_res:
        return None

    candidate = first_res["candidates"][0]
    content = candidate.get("content", {})
    parts = content.get("parts", [])

    tool_calls_executed = []
    function_calls = []

    for p in parts:
        if "functionCall" in p:
            function_calls.append(p["functionCall"])

    # If Gemini requested function calls
    if function_calls:
        contents.append(content)  # Append model's function call message
        
        response_parts = []
        for fc in function_calls[:settings.MAX_TOOL_CALLS_PER_TURN]:
            fname = fc.get("name")
            fargs = fc.get("args", {})
            result = execute_tool_call(fname, fargs)
            tool_calls_executed.append({
                "tool": fname,
                "args": fargs,
                "result": result
            })
            response_parts.append({
                "functionResponse": {
                    "name": fname,
                    "response": {"name": fname, "content": result}
                }
            })

        contents.append({
            "role": "function",
            "parts": response_parts
        })

        # Second turn: send function execution results back to Gemini
        follow_payload = {
            "systemInstruction": {
                "parts": [{"text": SYSTEM_PROMPT}]
            },
            "contents": contents,
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 800
            }
        }
        second_res = call_gemini_api(follow_payload)
        if second_res and "candidates" in second_res:
            final_cand = second_res["candidates"][0]
            final_parts = final_cand.get("content", {}).get("parts", [])
            final_text = "".join(p.get("text", "") for p in final_parts).strip()
            return {
                "text": final_text,
                "tool_calls": tool_calls_executed
            }

    # If Gemini answered directly with text
    final_text = "".join(p.get("text", "") for p in parts if "text" in p).strip()
    if final_text:
        return {
            "text": final_text,
            "tool_calls": tool_calls_executed
        }

    return None
