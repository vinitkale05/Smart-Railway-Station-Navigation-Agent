from starlette.requests import Request
from starlette.responses import JSONResponse
from backend.models.database import get_connection

async def get_train(request: Request):
    train_no = request.path_params["train_no"]
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM trains WHERE train_no = ?", (train_no,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        return JSONResponse({"error": f"Train {train_no} not found"}, status_code=404)
        
    t = dict(row)
    plat_str = t["current_platform"] or t["default_platform"]
    plat_num = plat_str.replace("Platform ", "").strip()
    return JSONResponse({
        "train_no": t["train_no"],
        "name": t["name"],
        "origin": t["origin"],
        "destination": t["destination"],
        "scheduled_departure": t["scheduled_departure"],
        "platform": plat_str,
        "platform_node_id": f"platform_{plat_num}_mid",
        "delay_minutes": t["delay_minutes"],
        "status": t["status"]
    })

async def list_trains(request: Request):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM trains ORDER BY scheduled_departure ASC")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return JSONResponse(rows)
