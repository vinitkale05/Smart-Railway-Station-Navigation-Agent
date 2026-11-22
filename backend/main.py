import os
from starlette.applications import Starlette
from starlette.routing import Route, WebSocketRoute, Mount
from starlette.responses import JSONResponse, FileResponse
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from backend.config import settings
from backend.data.seed_data import seed_database
from backend.models.database import get_connection

from backend.api.stations import list_stations, get_station_graph, list_facilities
from backend.api.trains import get_train, list_trains
from backend.api.sessions import create_session, get_session, send_message, compute_route, advance_step, get_logs
from backend.api.admin import admin_login, publish_platform_change, publish_closure, list_admin_history, get_disruptions
from backend.api.websocket import websocket_session_endpoint

async def health_check(request):
    return JSONResponse({
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    })

async def serve_spa_index(request):
    candidates = [
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "public", "index.html"),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "static_spa", "index.html")
    ]
    for static_index in candidates:
        if os.path.exists(static_index):
            return FileResponse(static_index)
    return JSONResponse({"message": "Smart Railway Station Navigation Agent API Running."})

routes = [
    Route("/health", health_check, methods=["GET"]),
    Route("/", serve_spa_index, methods=["GET"]),
    
    # Sessions
    Route("/api/sessions", create_session, methods=["POST"]),
    Route("/api/sessions/{id}", get_session, methods=["GET"]),
    Route("/api/sessions/{id}/messages", send_message, methods=["POST"]),
    Route("/api/sessions/{id}/route", compute_route, methods=["POST"]),
    Route("/api/sessions/{id}/step", advance_step, methods=["POST"]),
    Route("/api/sessions/{id}/logs", get_logs, methods=["GET"]),
    
    # Stations & Map Graph
    Route("/api/stations", list_stations, methods=["GET"]),
    Route("/api/stations/{id}/graph", get_station_graph, methods=["GET"]),
    Route("/api/stations/{id}/facilities", list_facilities, methods=["GET"]),
    
    # Trains
    Route("/api/trains", list_trains, methods=["GET"]),
    Route("/api/trains/{train_no}", get_train, methods=["GET"]),
    
    # Admin
    Route("/api/admin/login", admin_login, methods=["POST"]),
    Route("/api/admin/platform-changes", publish_platform_change, methods=["POST"]),
    Route("/api/admin/closures", publish_closure, methods=["POST"]),
    Route("/api/admin/history", list_admin_history, methods=["GET"]),
    Route("/api/disruptions", get_disruptions, methods=["GET"]),
    
    # WebSocket
    WebSocketRoute("/ws/sessions/{id}", websocket_session_endpoint)
]

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
]

from contextlib import asynccontextmanager

def startup():
    # Verify DB initialization
    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM stations")
        cnt = c.fetchone()[0]
        conn.close()
        if cnt == 0:
            seed_database()
    except Exception:
        seed_database()

@asynccontextmanager
async def lifespan(app):
    startup()
    yield

app = Starlette(
    debug=True,
    routes=routes,
    middleware=middleware,
    lifespan=lifespan
)
