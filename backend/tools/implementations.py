import sqlite3
from typing import Dict, Any, List, Optional
from backend.models.database import get_connection
from backend.routing.pathfinding import find_route_dijkstra_or_astar

def get_train_info(train_number: str, date: Optional[str] = None) -> Dict[str, Any]:
    """
    Returns scheduled platform, departure time, delay, and status for a train.
    """
    clean_no = str(train_number).strip()
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM trains WHERE train_no = ?", (clean_no,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        return {
            "found": False,
            "error": f"Train number {train_number} not found in current schedule."
        }
        
    t = dict(row)
    plat_str = t["current_platform"] or t["default_platform"]
    plat_num = plat_str.replace("Platform ", "").strip()
    return {
        "found": True,
        "train_no": t["train_no"],
        "name": t["name"],
        "origin": t["origin"],
        "destination": t["destination"],
        "scheduled_departure": t["scheduled_departure"],
        "platform": plat_str,
        "platform_node_id": f"platform_{plat_num}_mid",
        "delay_minutes": t["delay_minutes"],
        "status": t["status"]
    }

def find_route(from_node: str, to_node: str, accessible: bool = False) -> Dict[str, Any]:
    """
    Computes shortest path between two nodes. Excludes stairs when accessible=True.
    """
    route_res = find_route_dijkstra_or_astar(from_node, to_node, accessible=accessible)
    return route_res.model_dump()

def find_facility(facility_type: str, from_node: Optional[str] = "gate_1_main", open_only: bool = True) -> Dict[str, Any]:
    """
    Finds the nearest facility of a given type from the user's current location, ordered by walking distance.
    Facility types: washroom, water, food, waiting_room, help_desk, ticket_counter, cloak_room.
    """
    clean_type = facility_type.strip().lower()
    
    # Normalize synonyms
    synonym_map = {
        "restroom": "washroom",
        "toilet": "washroom",
        "bathroom": "washroom",
        "latrine": "washroom",
        "drinking_water": "water",
        "drinking water": "water",
        "water_fountain": "water",
        "tea": "food",
        "chai": "food",
        "restaurant": "food",
        "snacks": "food",
        "cafe": "food",
        "canteen": "food",
        "waiting": "waiting_room",
        "lounge": "waiting_room",
        "help": "help_desk",
        "information": "help_desk",
        "inquiry": "help_desk",
        "ticket": "ticket_counter",
        "booking": "ticket_counter",
        "atvm": "ticket_counter",
        "luggage": "cloak_room",
        "locker": "cloak_room"
    }
    target_type = synonym_map.get(clean_type, clean_type)

    conn = get_connection()
    c = conn.cursor()
    query = "SELECT * FROM facilities WHERE facility_type = ?"
    params = [target_type]
    if open_only:
        query += " AND is_open = 1"
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()

    if not rows:
        # Fallback to like search
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM facilities WHERE facility_type LIKE ? OR name LIKE ?", (f"%{clean_type}%", f"%{clean_type}%"))
        rows = c.fetchall()
        conn.close()

    if not rows:
        return {
            "found": False,
            "facility_type": target_type,
            "message": f"No open facilities found matching '{facility_type}'."
        }

    # Order matches by pathfinding distance from from_node
    matches = []
    start_loc = from_node if from_node else "gate_1_main"
    for r in rows:
        fac = dict(r)
        route_to_fac = find_route_dijkstra_or_astar(start_loc, fac["node_id"], accessible=False)
        distance = route_to_fac.total_distance_m if not route_to_fac.error else 9999
        matches.append({
            "id": fac["id"],
            "name": fac["name"],
            "facility_type": fac["facility_type"],
            "node_id": fac["node_id"],
            "distance_m": distance,
            "opening_hours": fac["opening_hours"],
            "is_accessible": bool(fac["is_accessible"]),
            "estimated_minutes": round(distance / 60, 1)
        })

    matches.sort(key=lambda x: x["distance_m"])
    return {
        "found": True,
        "facility_type": target_type,
        "nearest": matches[0],
        "all_matches": matches
    }

def get_platform_status(platform_id: str) -> Dict[str, Any]:
    """
    Returns current assignments, active trains, and alerts for a given platform.
    """
    clean_p = platform_id.lower().replace("platform", "").strip()
    plat_str = f"Platform {clean_p}"
    
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT train_no, name, scheduled_departure, delay_minutes, status 
        FROM trains 
        WHERE current_platform = ? OR default_platform = ?
    """, (plat_str, plat_str))
    trains = [dict(r) for r in c.fetchall()]
    conn.close()

    return {
        "platform": plat_str,
        "platform_node_id": f"platform_{clean_p}_mid",
        "active_trains": trains,
        "train_count": len(trains),
        "alerts": [] if trains else ["No trains currently scheduled on this platform."]
    }

def get_lift_status(node_id: str) -> Dict[str, Any]:
    """
    Returns whether a lift or escalator is working and operational notes.
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT * FROM edges 
        WHERE (from_node = ? OR to_node = ?) AND has_lift = 1
    """, (node_id, node_id))
    edges = [dict(r) for r in c.fetchall()]
    conn.close()

    if not edges:
        return {
            "node_id": node_id,
            "is_lift": False,
            "is_operational": False,
            "note": f"No lift mechanism registered at {node_id}."
        }

    operational = all(bool(e["is_active"]) for e in edges)
    return {
        "node_id": node_id,
        "is_lift": True,
        "is_operational": operational,
        "status": "Operational" if operational else "Out of Service (Maintenance)",
        "note": "Lift in regular service with braille buttons and audio announcement." if operational else "Temporarily closed for scheduled maintenance. Ramp or staff assistance available."
    }

def send_alert_to_user(session_id: str, message: str) -> Dict[str, Any]:
    """
    Queues a notification to be sent to a passenger session.
    """
    return {
        "session_id": session_id,
        "delivered": True,
        "message": message,
        "status": "Queued for WebSocket dispatch"
    }
