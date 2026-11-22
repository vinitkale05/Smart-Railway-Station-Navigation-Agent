import uuid
from datetime import datetime
from starlette.requests import Request
from starlette.responses import JSONResponse
from backend.models.database import db_save_session, db_get_session, db_get_session_logs
from backend.agent.agent_loop import run_agent_loop
from backend.routing.pathfinding import find_route_dijkstra_or_astar

async def create_session(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}
        
    session_id = str(uuid.uuid4())[:8]
    session_data = {
        "id": session_id,
        "station_id": body.get("station_id", "pune_junction"),
        "train_no": body.get("train_no"),
        "accessibility_prefs": bool(body.get("accessibility_prefs", False)),
        "current_node_id": body.get("current_node_id", "gate_1_main"),
        "destination_node_id": body.get("destination_node_id"),
        "active_route": None,
        "current_step_index": 0,
        "created_at": datetime.now().isoformat()
    }
    db_save_session(session_data)
    return JSONResponse(session_data, status_code=201)

async def get_session(request: Request):
    session_id = request.path_params["id"]
    sess = db_get_session(session_id)
    if not sess:
        return JSONResponse({"error": "Session not found"}, status_code=404)
    return JSONResponse(sess)

async def send_message(request: Request):
    session_id = request.path_params["id"]
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON body"}, status_code=400)
        
    msg = body.get("message", "")
    if not msg:
        return JSONResponse({"error": "Message is required"}, status_code=400)
        
    response = run_agent_loop(session_id, msg)
    return JSONResponse(response.model_dump())

async def compute_route(request: Request):
    session_id = request.path_params["id"]
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid JSON body"}, status_code=400)
        
    from_node = body.get("from_node")
    to_node = body.get("to_node")
    accessible = body.get("accessible", False)
    
    sess = db_get_session(session_id)
    if sess:
        if not from_node:
            from_node = sess.get("current_node_id", "gate_1_main")
        if "accessible" not in body:
            accessible = sess.get("accessibility_prefs", False)

    if not from_node or not to_node:
        return JSONResponse({"error": "from_node and to_node are required"}, status_code=400)

    route_res = find_route_dijkstra_or_astar(from_node, to_node, accessible=accessible)
    
    if sess:
        sess["current_node_id"] = from_node
        sess["destination_node_id"] = to_node
        sess["active_route"] = route_res.model_dump()
        sess["current_step_index"] = 0
        db_save_session(sess)

    return JSONResponse(route_res.model_dump())

async def advance_step(request: Request):
    session_id = request.path_params["id"]
    sess = db_get_session(session_id)
    if not sess:
        return JSONResponse({"error": "Session not found"}, status_code=404)
        
    active_route = sess.get("active_route")
    if not active_route or not active_route.get("steps"):
        return JSONResponse({"error": "No active route to advance"}, status_code=400)
        
    steps = active_route["steps"]
    curr = sess.get("current_step_index", 0)
    
    if curr < len(steps) - 1:
        sess["current_step_index"] = curr + 1
        # Update current location to step to_node_id
        sess["current_node_id"] = steps[curr]["to_node_id"]
        completed = False
    else:
        sess["current_step_index"] = len(steps)
        sess["current_node_id"] = steps[-1]["to_node_id"]
        completed = True
        
    db_save_session(sess)
    return JSONResponse({
        "current_step_index": sess["current_step_index"],
        "current_node_id": sess["current_node_id"],
        "completed": completed,
        "total_steps": len(steps)
    })

async def get_logs(request: Request):
    session_id = request.path_params["id"]
    logs = db_get_session_logs(session_id)
    return JSONResponse(logs)
