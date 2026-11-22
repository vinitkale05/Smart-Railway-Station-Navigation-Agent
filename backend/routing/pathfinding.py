import math
import networkx as nx
from typing import List, Optional, Tuple, Dict, Any
from backend.models.schemas import RouteResult, RouteStep
from backend.routing.graph_loader import load_station_graph

def euclidean_distance_heuristic(u: str, v: str, graph: nx.Graph) -> float:
    """
    Euclidean straight-line distance heuristic for A* pathfinding.
    """
    u_data = graph.nodes.get(u, {})
    v_data = graph.nodes.get(v, {})
    
    if "x" in u_data and "x" in v_data:
        dx = u_data["x"] - v_data["x"]
        dy = u_data["y"] - v_data["y"]
        return math.sqrt(dx * dx + dy * dy)
    return 0.0

def generate_step_instruction(from_node_id: str, to_node_id: str, edge_data: Dict[str, Any], from_node: Dict[str, Any], to_node: Dict[str, Any]) -> Tuple[str, str]:
    """
    Generates human-readable instruction and icon for a step in the route.
    """
    to_label = to_node.get("label", to_node_id)
    to_type = to_node.get("type", "")
    has_stairs = edge_data.get("has_stairs", False)
    has_lift = edge_data.get("has_lift", False)
    
    if has_lift:
        icon = "lift"
        instruction = f"Take the lift to {to_label}."
    elif has_stairs:
        icon = "stairs"
        instruction = f"Take the stairs up/down towards {to_label}."
    elif to_type == "ramp":
        icon = "ramp"
        instruction = f"Proceed along the step-free ramp to {to_label}."
    elif "footbridge" in to_type or "fob" in to_node_id:
        icon = "walk"
        instruction = f"Walk across the footbridge to {to_label}."
    elif to_type == "platform":
        icon = "destination"
        instruction = f"Proceed onto {to_label} to reach boarding area."
    elif to_type == "washroom":
        icon = "destination"
        instruction = f"Arrive at {to_label}."
    elif to_type == "food":
        icon = "food"
        instruction = f"Reach {to_label}."
    elif to_type == "waiting":
        icon = "waiting"
        instruction = f"Enter {to_label}."
    elif to_type == "gate":
        icon = "gate"
        instruction = f"Proceed through {to_label}."
    else:
        icon = "walk"
        instruction = f"Walk straight towards {to_label}."
        
    return instruction, icon

def find_route_dijkstra_or_astar(
    from_node: str,
    to_node: str,
    accessible: bool = False,
    use_astar: bool = True,
    station_id: str = "pune_junction",
    graph: Optional[nx.Graph] = None
) -> RouteResult:
    """
    Calculates the shortest or accessible path between two nodes using Dijkstra or A*.
    Guarantees:
    - Never uses restricted nodes (e.g. track zones)
    - Excludes stairs-only paths when accessible=True
    - Avoids inactive edges (e.g. broken lifts)
    - Returns structured RouteResult with steps and timings
    """
    if graph is None:
        graph = load_station_graph(station_id)
        
    if from_node not in graph:
        return RouteResult(
            from_node=from_node,
            to_node=to_node,
            total_distance_m=0,
            total_estimated_seconds=0,
            is_accessible=accessible,
            nodes=[],
            steps=[],
            error=f"Start node '{from_node}' does not exist in station graph."
        )
        
    if to_node not in graph:
        return RouteResult(
            from_node=from_node,
            to_node=to_node,
            total_distance_m=0,
            total_estimated_seconds=0,
            is_accessible=accessible,
            nodes=[],
            steps=[],
            error=f"Destination node '{to_node}' does not exist in station graph."
        )

    # Filter subgraph: remove restricted nodes, inactive edges, and stairs when accessible is True
    valid_subgraph = nx.Graph()
    for n, data in graph.nodes(data=True):
        if not data.get("is_restricted", False):
            valid_subgraph.add_node(n, **data)
            
    for u, v, data in graph.edges(data=True):
        if u not in valid_subgraph or v not in valid_subgraph:
            continue
        if not data.get("is_active", True):
            continue
        if accessible:
            # When accessible routing requested, reject stairs-only paths
            if data.get("has_stairs", False) and not data.get("has_lift", False):
                continue
            if not data.get("is_step_free", True) and not data.get("has_lift", False):
                continue
        valid_subgraph.add_edge(u, v, **data)

    try:
        if use_astar and "x" in graph.nodes[from_node] and "x" in graph.nodes[to_node]:
            path = nx.astar_path(
                valid_subgraph,
                from_node,
                to_node,
                heuristic=lambda u, v: euclidean_distance_heuristic(u, v, valid_subgraph),
                weight="distance_m"
            )
        else:
            path = nx.dijkstra_path(
                valid_subgraph,
                from_node,
                to_node,
                weight="distance_m"
            )
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return RouteResult(
            from_node=from_node,
            to_node=to_node,
            total_distance_m=0,
            total_estimated_seconds=0,
            is_accessible=accessible,
            nodes=[],
            steps=[],
            error=f"No {'step-free ' if accessible else ''}route found between {from_node} and {to_node}."
        )

    # Build steps
    steps: List[RouteStep] = []
    total_dist = 0.0
    total_seconds = 0
    walking_speed_mps = 0.85 if accessible else 1.15  # meters per second

    for i in range(len(path) - 1):
        u = path[i]
        v = path[i + 1]
        edge_data = valid_subgraph.get_edge_data(u, v, default={})
        dist = float(edge_data.get("distance_m", 10.0))
        total_dist += dist
        
        # Lift vertical time penalty ~ 30s, stairs ~ 20s
        step_seconds = int(dist / walking_speed_mps)
        if edge_data.get("has_lift"):
            step_seconds += 25
        elif edge_data.get("has_stairs"):
            step_seconds += 15
        total_seconds += step_seconds

        u_node = valid_subgraph.nodes[u]
        v_node = valid_subgraph.nodes[v]
        instruction, icon = generate_step_instruction(u, v, edge_data, u_node, v_node)

        steps.append(RouteStep(
            step_number=i + 1,
            instruction=instruction,
            from_node_id=u,
            to_node_id=v,
            distance_m=round(dist, 1),
            estimated_seconds=step_seconds,
            is_step_free=bool(edge_data.get("is_step_free", True)),
            has_stairs=bool(edge_data.get("has_stairs", False)),
            has_lift=bool(edge_data.get("has_lift", False)),
            icon=icon
        ))

    return RouteResult(
        from_node=from_node,
        to_node=to_node,
        total_distance_m=round(total_dist, 1),
        total_estimated_seconds=total_seconds,
        is_accessible=accessible,
        nodes=path,
        steps=steps,
        error=None
    )
