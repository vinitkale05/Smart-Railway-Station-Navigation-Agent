from starlette.requests import Request
from starlette.responses import JSONResponse
from backend.models.database import get_connection

async def list_stations(request: Request):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM stations")
    stations = [dict(r) for r in c.fetchall()]
    conn.close()
    return JSONResponse(stations)

async def get_station_graph(request: Request):
    station_id = request.path_params["id"]
    conn = get_connection()
    c = conn.cursor()
    
    c.execute("SELECT * FROM stations WHERE id = ?", (station_id,))
    st_row = c.fetchone()
    if not st_row:
        conn.close()
        return JSONResponse({"error": "Station not found"}, status_code=404)
        
    c.execute("SELECT * FROM nodes WHERE station_id = ?", (station_id,))
    nodes = [dict(r) for r in c.fetchall()]
    for n in nodes:
        n["is_restricted"] = bool(n["is_restricted"])
        
    c.execute("""
        SELECT e.* FROM edges e 
        JOIN nodes n ON e.from_node = n.id 
        WHERE n.station_id = ?
    """, (station_id,))
    edges = [dict(r) for r in c.fetchall()]
    for e in edges:
        e["has_stairs"] = bool(e["has_stairs"])
        e["has_lift"] = bool(e["has_lift"])
        e["is_step_free"] = bool(e["is_step_free"])
        e["is_active"] = bool(e["is_active"])
        
    conn.close()
    return JSONResponse({
        "station": dict(st_row),
        "nodes": nodes,
        "edges": edges
    })

async def list_facilities(request: Request):
    station_id = request.path_params["id"]
    fac_type = request.query_params.get("type")
    
    conn = get_connection()
    c = conn.cursor()
    if fac_type:
        c.execute("""
            SELECT f.*, n.label as node_label, n.x, n.y 
            FROM facilities f
            JOIN nodes n ON f.node_id = n.id
            WHERE n.station_id = ? AND f.facility_type = ?
        """, (station_id, fac_type))
    else:
        c.execute("""
            SELECT f.*, n.label as node_label, n.x, n.y 
            FROM facilities f
            JOIN nodes n ON f.node_id = n.id
            WHERE n.station_id = ?
        """, (station_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    for r in rows:
        r["is_open"] = bool(r["is_open"])
        r["is_accessible"] = bool(r["is_accessible"])
    return JSONResponse(rows)
