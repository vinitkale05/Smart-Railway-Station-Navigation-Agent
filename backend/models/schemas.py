from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

# --- Station & Graph Models ---
class StationBase(BaseModel):
    id: str
    name: str
    city: str
    timezone: str = "Asia/Kolkata"

class Station(StationBase):
    pass

class NodeBase(BaseModel):
    id: str
    station_id: str
    type: str  # gate, concourse, platform, stairs, lift, washroom, food, waiting, help_desk, footbridge, ticket_counter, ramp
    label: str
    x: float
    y: float
    is_restricted: bool = False
    metadata: Optional[Dict[str, Any]] = None

class Node(NodeBase):
    pass

class EdgeBase(BaseModel):
    id: str
    from_node: str
    to_node: str
    distance_m: float
    has_stairs: bool = False
    has_lift: bool = False
    is_step_free: bool = True
    is_active: bool = True

class Edge(EdgeBase):
    pass

class StationGraph(BaseModel):
    station: Station
    nodes: List[Node]
    edges: List[Edge]

# --- Train & Platform Models ---
class TrainBase(BaseModel):
    train_no: str
    name: str
    origin: str
    destination: str
    scheduled_departure: str
    default_platform: str

class Train(TrainBase):
    current_platform: Optional[str] = None
    delay_minutes: int = 0
    status: str = "On Time"  # On Time, Delayed, Platform Changed, Arrived, Departed

class PlatformAssignment(BaseModel):
    id: Optional[str] = None
    train_no: str
    platform_node_id: str
    effective_from: str
    source: str = "schedule"  # schedule or admin
    delay_minutes: int = 0

# --- Facility Model ---
class Facility(BaseModel):
    id: str
    node_id: str
    facility_type: str  # washroom, water, food, waiting_room, help_desk, ticket_counter, cloak_room, wheelchair_booth
    name: str
    is_open: bool = True
    opening_hours: str = "24x7"
    is_accessible: bool = True

# --- Navigation & Routing Models ---
class RouteStep(BaseModel):
    step_number: int
    instruction: str
    from_node_id: str
    to_node_id: str
    distance_m: float
    estimated_seconds: int
    is_step_free: bool
    has_stairs: bool
    has_lift: bool
    icon: Optional[str] = "walk"  # walk, stairs, lift, ramp, destination

class RouteResult(BaseModel):
    from_node: str
    to_node: str
    total_distance_m: float
    total_estimated_seconds: int
    is_accessible: bool
    nodes: List[str]
    steps: List[RouteStep]
    error: Optional[str] = None

# --- Session & Chat Models ---
class SessionCreate(BaseModel):
    station_id: str = "pune_junction"
    train_no: Optional[str] = None
    accessibility_prefs: bool = False  # requires step-free / lift routes
    current_node_id: Optional[str] = "gate_1_main"
    destination_node_id: Optional[str] = None

class Session(BaseModel):
    id: str
    station_id: str
    train_no: Optional[str] = None
    accessibility_prefs: bool = False
    current_node_id: Optional[str] = None
    destination_node_id: Optional[str] = None
    active_route: Optional[RouteResult] = None
    current_step_index: int = 0
    created_at: str

class MessageSend(BaseModel):
    message: str

class QuickAction(BaseModel):
    label: str
    action: str  # e.g., "start_navigation", "find_washroom", "train_status"
    payload: Optional[Dict[str, Any]] = None

class MessageResponse(BaseModel):
    text: str
    tool_calls: List[Dict[str, Any]] = []
    route: Optional[RouteResult] = None
    train_info: Optional[Dict[str, Any]] = None
    facility_info: Optional[List[Dict[str, Any]]] = None
    quick_actions: List[QuickAction] = []
    needs_clarification: bool = False
    clarification_prompt: Optional[str] = None

# --- Admin Models ---
class PlatformChangeRequest(BaseModel):
    train_no: str
    new_platform: str  # e.g. "Platform 3" or node id "platform_3_mid"
    delay_minutes: int = 0
    reason: Optional[str] = "Operational adjustment"

class ClosureRequest(BaseModel):
    node_id: str
    is_closed: bool = True
    reason: Optional[str] = "Maintenance work"

class AdminLoginRequest(BaseModel):
    username: str
    password: str

class AdminLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# --- WebSocket Event Model ---
class WSEvent(BaseModel):
    event_type: str  # "platform_change", "closure_alert", "route_recalculated", "system_notice"
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
