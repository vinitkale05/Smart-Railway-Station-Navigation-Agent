export interface Station {
  id: string;
  name: string;
  city: string;
  timezone: string;
}

export interface Node {
  id: string;
  station_id: string;
  type: string;
  label: string;
  x: number;
  y: number;
  is_restricted: boolean;
}

export interface Edge {
  id: string;
  from_node: string;
  to_node: string;
  distance_m: number;
  has_stairs: boolean;
  has_lift: boolean;
  is_step_free: boolean;
  is_active: boolean;
}

export interface StationGraph {
  station: Station;
  nodes: Node[];
  edges: Edge[];
}

export interface RouteStep {
  step_number: number;
  instruction: string;
  from_node_id: string;
  to_node_id: string;
  distance_m: number;
  estimated_seconds: number;
  is_step_free: boolean;
  has_stairs: boolean;
  has_lift: boolean;
  icon?: string;
}

export interface RouteResult {
  from_node: string;
  to_node: string;
  total_distance_m: number;
  total_estimated_seconds: number;
  is_accessible: boolean;
  nodes: string[];
  steps: RouteStep[];
  error?: string | null;
}

export interface QuickAction {
  label: string;
  action: string;
  payload?: Record<string, any>;
}

export interface MessageResponse {
  text: string;
  tool_calls: Array<{ tool: string; args: any; result: any }>;
  route?: RouteResult;
  train_info?: any;
  facility_info?: any[];
  quick_actions?: QuickAction[];
  needs_clarification?: boolean;
  clarification_prompt?: string;
}

export interface Train {
  train_no: string;
  name: string;
  origin: string;
  destination: string;
  scheduled_departure: string;
  default_platform: string;
  current_platform?: string;
  delay_minutes: number;
  status: string;
}

export interface WSEvent {
  event_type: string;
  title: string;
  message: string;
  data?: any;
  timestamp: string;
}
