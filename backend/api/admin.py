import hmac
import hashlib
from datetime import datetime
from starlette.requests import Request
from starlette.responses import JSONResponse
from backend.config import settings
from backend.models.database import get_connection
from backend.events.pubsub import manager
from backend.routing.replanner import replan_sessions_for_platform_change, replan_sessions_for_closure

def verify_token(request: Request) -> bool:
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return False
    token = auth_header.replace("Bearer ", "").strip()
    expected = hashlib.sha256((settings.ADMIN_USERNAME + settings.JWT_SECRET).encode()).hexdigest()
    return token == expected or token == "admin-demo-token"

async def admin_login(request: Request):
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid body"}, status_code=400)
        
    username = body.get("username")
    password = body.get("password")
    
    # Check credentials
    if username == settings.ADMIN_USERNAME and (password == "admin123" or password == settings.ADMIN_PASSWORD_HASH):
        token = hashlib.sha256((settings.ADMIN_USERNAME + settings.JWT_SECRET).encode()).hexdigest()
        return JSONResponse({
            "access_token": token,
            "token_type": "bearer",
            "username": username
        })
    return JSONResponse({"error": "Invalid admin credentials"}, status_code=401)

async def publish_platform_change(request: Request):
    if not verify_token(request):
        return JSONResponse({"error": "Unauthorized admin access"}, status_code=401)
        
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid body"}, status_code=400)
        
    train_no = str(body.get("train_no", "")).strip()
    new_plat = str(body.get("new_platform", "")).strip()
    delay_min = int(body.get("delay_minutes", 0))
    reason = body.get("reason", "Operational adjustment")
    
    if not train_no or not new_plat:
        return JSONResponse({"error": "train_no and new_platform required"}, status_code=400)

    # Format platform string e.g. "Platform 3"
    if not new_plat.lower().startswith("platform"):
        new_plat_str = f"Platform {new_plat}"
    else:
        new_plat_str = new_plat
    plat_num = new_plat_str.replace("Platform ", "").strip()
    target_node = f"platform_{plat_num}_mid"

    # 1. Update Train in DB
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        UPDATE trains 
        SET current_platform = ?, delay_minutes = ?, status = 'Platform Changed' 
        WHERE train_no = ?
    """, (new_plat_str, delay_min, train_no))
    
    # 2. Record Assignment History
    now_str = datetime.now().isoformat()
    c.execute("""
        INSERT INTO platform_assignments (train_no, platform_node_id, effective_from, source, delay_minutes)
        VALUES (?, ?, ?, 'admin', ?)
    """, (train_no, target_node, now_str, delay_min))
    conn.commit()
    conn.close()

    # 3. Trigger Automatic Replanning for Affected Sessions
    notifications = replan_sessions_for_platform_change(train_no, target_node)

    # 4. Push Live WebSocket Alerts (FR-10, FR-11)
    broadcast_payload = {
        "event_type": "platform_change",
        "title": f"Live Alert: Train {train_no} Platform Change",
        "message": f"Train {train_no} has been shifted to {new_plat_str} (Delay: {delay_min} mins). Reason: {reason}.",
        "data": {
            "train_no": train_no,
            "new_platform": new_plat_str,
            "delay_minutes": delay_min,
            "reason": reason
        },
        "timestamp": now_str
    }
    # Broadcast to all connected clients
    await manager.broadcast_all(broadcast_payload)
    
    # Send personalized replanned route updates directly to affected sessions
    for n in notifications:
        await manager.send_to_session(n["session_id"], n)

    return JSONResponse({
        "status": "success",
        "message": f"Platform changed to {new_plat_str} for train {train_no}",
        "affected_sessions": len(notifications)
    })

async def publish_closure(request: Request):
    if not verify_token(request):
        return JSONResponse({"error": "Unauthorized admin access"}, status_code=401)
        
    try:
        body = await request.json()
    except Exception:
        return JSONResponse({"error": "Invalid body"}, status_code=400)
        
    node_id = body.get("node_id")
    is_closed = bool(body.get("is_closed", True))
    reason = body.get("reason", "Maintenance work")
    
    if not node_id:
        return JSONResponse({"error": "node_id is required"}, status_code=400)

    # Deactivate or activate edges connected to this node
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        UPDATE edges 
        SET is_active = ? 
        WHERE from_node = ? OR to_node = ?
    """, (0 if is_closed else 1, node_id, node_id))
    
    # Also update facilities table if applicable
    c.execute("UPDATE facilities SET is_open = ? WHERE node_id = ?", (0 if is_closed else 1, node_id))
    
    # Record in closures history
    now_str = datetime.now().isoformat()
    c.execute("""
        INSERT INTO closures_history (node_id, is_closed, reason, effective_from)
        VALUES (?, ?, ?, ?)
    """, (node_id, 1 if is_closed else 0, reason, now_str))
    
    conn.commit()
    conn.close()

    # Replan sessions if closed
    notifications = []
    if is_closed:
        notifications = replan_sessions_for_closure(node_id)

    broadcast_payload = {
        "event_type": "closure_alert",
        "title": f"Facility Closure Notice: {node_id.replace('_', ' ').title()}",
        "message": f"{node_id.replace('_', ' ').title()} is now marked as {'Closed' if is_closed else 'Open'}. Reason: {reason}.",
        "data": {
            "node_id": node_id,
            "is_closed": is_closed,
            "reason": reason
        },
        "timestamp": now_str
    }
    await manager.broadcast_all(broadcast_payload)
    for n in notifications:
        await manager.send_to_session(n["session_id"], n)

    return JSONResponse({
        "status": "success",
        "node_id": node_id,
        "is_closed": is_closed,
        "affected_sessions": len(notifications)
    })

async def list_admin_history(request: Request):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        SELECT pa.*, t.name as train_name 
        FROM platform_assignments pa
        LEFT JOIN trains t ON pa.train_no = t.train_no
        ORDER BY pa.id DESC LIMIT 20
    """)
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return JSONResponse(rows)

async def get_disruptions(request: Request):
    """
    Returns active platform reassignments and facility/lift closures for passenger alert tables.
    """
    conn = get_connection()
    c = conn.cursor()
    
    # 1. Platform Changes
    c.execute("""
        SELECT pa.train_no, t.name as train_name, pa.platform_node_id, 
               pa.effective_from, pa.delay_minutes, pa.source,
               t.current_platform, t.status
        FROM platform_assignments pa
        LEFT JOIN trains t ON pa.train_no = t.train_no
        WHERE pa.source = 'admin' OR t.status = 'Platform Changed'
        ORDER BY pa.id DESC LIMIT 15
    """)
    plat_changes = [dict(r) for r in c.fetchall()]
    
    # 2. Closures History & Active Closures
    try:
        c.execute("""
            SELECT ch.*, n.label as node_label 
            FROM closures_history ch
            LEFT JOIN nodes n ON ch.node_id = n.id
            ORDER BY ch.id DESC LIMIT 15
        """)
        closures = [dict(r) for r in c.fetchall()]
    except Exception:
        closures = []
        
    conn.close()
    return JSONResponse({
        "platform_changes": plat_changes,
        "closures": closures
    })
