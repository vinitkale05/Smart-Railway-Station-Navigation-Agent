from typing import List, Dict, Any, Optional
from backend.models.database import db_get_all_active_sessions, db_save_session
from backend.routing.pathfinding import find_route_dijkstra_or_astar

def replan_sessions_for_platform_change(
    train_no: str,
    new_platform_node_id: str,
    station_id: str = "pune_junction"
) -> List[Dict[str, Any]]:
    """
    Finds active passenger sessions tracking this train, updates their destination to the new platform,
    recalculates their route, saves the session, and returns alerts to push via WebSocket.
    """
    sessions = db_get_all_active_sessions()
    notifications = []
    
    for s in sessions:
        if s.get("train_no") == train_no:
            current_loc = s.get("current_node_id", "gate_1_main")
            accessible = s.get("accessibility_prefs", False)
            
            # Recalculate route from passenger's current position to the new platform node
            new_route = find_route_dijkstra_or_astar(
                from_node=current_loc,
                to_node=new_platform_node_id,
                accessible=accessible,
                station_id=station_id
            )
            
            s["destination_node_id"] = new_platform_node_id
            s["active_route"] = new_route.model_dump()
            s["current_step_index"] = 0
            db_save_session(s)
            
            notifications.append({
                "session_id": s["id"],
                "event_type": "platform_change",
                "title": f"Platform Change Alert: Train {train_no}",
                "message": f"Attention: Train {train_no} platform has been reassigned to {new_platform_node_id.replace('_', ' ').title()}. Your route has been automatically recalculated.",
                "data": {
                    "train_no": train_no,
                    "new_platform_node": new_platform_node_id,
                    "new_route": new_route.model_dump()
                }
            })
            
    return notifications

def replan_sessions_for_closure(
    closed_node_id: str,
    station_id: str = "pune_junction"
) -> List[Dict[str, Any]]:
    """
    Finds active sessions whose route passes through a closed node or lift,
    recalculates their path bypassing the closure, and returns notifications.
    """
    sessions = db_get_all_active_sessions()
    notifications = []
    
    for s in sessions:
        active_route = s.get("active_route")
        if not active_route:
            continue
            
        nodes = active_route.get("nodes", [])
        if closed_node_id in nodes:
            current_loc = s.get("current_node_id", "gate_1_main")
            destination = s.get("destination_node_id")
            if not destination:
                continue
                
            accessible = s.get("accessibility_prefs", False)
            new_route = find_route_dijkstra_or_astar(
                from_node=current_loc,
                to_node=destination,
                accessible=accessible,
                station_id=station_id
            )
            
            s["active_route"] = new_route.model_dump()
            s["current_step_index"] = 0
            db_save_session(s)
            
            notifications.append({
                "session_id": s["id"],
                "event_type": "closure_alert",
                "title": "Route Update: Facility / Path Closed",
                "message": f"Notice: Node {closed_node_id.replace('_', ' ')} is currently closed. A detour has been planned.",
                "data": {
                    "closed_node": closed_node_id,
                    "new_route": new_route.model_dump()
                }
            })
            
    return notifications
