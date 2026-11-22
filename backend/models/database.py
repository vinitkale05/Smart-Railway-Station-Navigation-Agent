import os
import shutil
import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from backend.config import settings

def get_db_path() -> str:
    """
    Returns the appropriate SQLite DB path.
    On Vercel and serverless platforms, root directory is read-only, so /tmp is used.
    """
    configured_path = settings.DATABASE_URL.replace("sqlite:///", "")
    
    # Check if running in Vercel or serverless environment
    if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME") or not os.access(os.path.dirname(os.path.abspath(configured_path)) or ".", os.W_OK):
        tmp_db = "/tmp/railway_station.db"
        if not os.path.exists(tmp_db):
            # If repo has pre-seeded DB, copy it
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            src_db = os.path.join(root_dir, "railway_station.db")
            if os.path.exists(src_db):
                try:
                    shutil.copyfile(src_db, tmp_db)
                except Exception:
                    pass
        return tmp_db
    return configured_path

def get_connection():
    conn = sqlite3.connect(get_db_path(), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Stations
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stations (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        city TEXT NOT NULL,
        timezone TEXT NOT NULL
    )
    """)
    
    # Nodes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS nodes (
        id TEXT PRIMARY KEY,
        station_id TEXT NOT NULL,
        type TEXT NOT NULL,
        label TEXT NOT NULL,
        x REAL NOT NULL,
        y REAL NOT NULL,
        is_restricted INTEGER DEFAULT 0,
        metadata TEXT
    )
    """)
    
    # Edges
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS edges (
        id TEXT PRIMARY KEY,
        from_node TEXT NOT NULL,
        to_node TEXT NOT NULL,
        distance_m REAL NOT NULL,
        has_stairs INTEGER DEFAULT 0,
        has_lift INTEGER DEFAULT 0,
        is_step_free INTEGER DEFAULT 1,
        is_active INTEGER DEFAULT 1
    )
    """)
    
    # Trains
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trains (
        train_no TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        origin TEXT NOT NULL,
        destination TEXT NOT NULL,
        scheduled_departure TEXT NOT NULL,
        default_platform TEXT NOT NULL,
        current_platform TEXT,
        delay_minutes INTEGER DEFAULT 0,
        status TEXT DEFAULT 'On Time'
    )
    """)
    
    # Platform Assignments History
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS platform_assignments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        train_no TEXT NOT NULL,
        platform_node_id TEXT NOT NULL,
        effective_from TEXT NOT NULL,
        source TEXT DEFAULT 'schedule',
        delay_minutes INTEGER DEFAULT 0
    )
    """)
    
    # Facilities
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS facilities (
        id TEXT PRIMARY KEY,
        node_id TEXT NOT NULL,
        facility_type TEXT NOT NULL,
        name TEXT NOT NULL,
        is_open INTEGER DEFAULT 1,
        opening_hours TEXT DEFAULT '24x7',
        is_accessible INTEGER DEFAULT 1
    )
    """)

    # Closures History
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS closures_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        node_id TEXT NOT NULL,
        is_closed INTEGER NOT NULL,
        reason TEXT,
        effective_from TEXT NOT NULL
    )
    """)
    
    # Sessions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        id TEXT PRIMARY KEY,
        station_id TEXT NOT NULL,
        train_no TEXT,
        accessibility_prefs INTEGER DEFAULT 0,
        current_node_id TEXT,
        destination_node_id TEXT,
        active_route TEXT,
        current_step_index INTEGER DEFAULT 0,
        created_at TEXT NOT NULL
    )
    """)
    
    # Conversation Logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversation_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        tool_calls TEXT,
        latency_ms INTEGER DEFAULT 0,
        created_at TEXT NOT NULL
    )
    """)
    
    conn.commit()
    conn.close()

# Session DB Helpers
def db_save_session(session_dict: Dict[str, Any]):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    INSERT OR REPLACE INTO sessions (
        id, station_id, train_no, accessibility_prefs, current_node_id, 
        destination_node_id, active_route, current_step_index, created_at
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session_dict["id"],
        session_dict["station_id"],
        session_dict.get("train_no"),
        1 if session_dict.get("accessibility_prefs") else 0,
        session_dict.get("current_node_id"),
        session_dict.get("destination_node_id"),
        json.dumps(session_dict.get("active_route")) if session_dict.get("active_route") else None,
        session_dict.get("current_step_index", 0),
        session_dict.get("created_at", datetime.now().isoformat())
    ))
    conn.commit()
    conn.close()

def db_get_session(session_id: str) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    d["accessibility_prefs"] = bool(d["accessibility_prefs"])
    if d.get("active_route"):
        try:
            d["active_route"] = json.loads(d["active_route"])
        except Exception:
            d["active_route"] = None
    return d

def db_get_all_active_sessions() -> List[Dict[str, Any]]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM sessions")
    rows = c.fetchall()
    conn.close()
    results = []
    for row in rows:
        d = dict(row)
        d["accessibility_prefs"] = bool(d["accessibility_prefs"])
        if d.get("active_route"):
            try:
                d["active_route"] = json.loads(d["active_route"])
            except Exception:
                d["active_route"] = None
        results.append(d)
    return results

def db_log_turn(session_id: str, role: str, content: str, tool_calls: Optional[List[Dict[str, Any]]] = None, latency_ms: int = 0):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
    INSERT INTO conversation_logs (session_id, role, content, tool_calls, latency_ms, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        session_id,
        role,
        content,
        json.dumps(tool_calls) if tool_calls else None,
        latency_ms,
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()

def db_get_session_logs(session_id: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM conversation_logs WHERE session_id = ? ORDER BY id ASC", (session_id,))
    rows = c.fetchall()
    conn.close()
    res = []
    for r in rows:
        d = dict(r)
        if d.get("tool_calls"):
            try:
                d["tool_calls"] = json.loads(d["tool_calls"])
            except Exception:
                pass
        res.append(d)
    return res
