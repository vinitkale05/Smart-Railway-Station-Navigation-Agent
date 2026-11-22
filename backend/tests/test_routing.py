import pytest
from backend.routing.pathfinding import find_route_dijkstra_or_astar
from backend.routing.graph_loader import load_station_graph
from backend.data.seed_data import seed_database

@pytest.fixture(autouse=True)
def setup_db():
    seed_database()

def test_graph_loading():
    G = load_station_graph("pune_junction")
    assert len(G.nodes) >= 30
    assert len(G.edges) >= 30
    assert "gate_1_main" in G.nodes
    assert "platform_1_mid" in G.nodes

def test_shortest_path_gate_to_platform():
    route = find_route_dijkstra_or_astar("gate_1_main", "platform_1_mid", accessible=False)
    assert route.error is None
    assert route.total_distance_m > 0
    assert len(route.nodes) >= 3
    assert route.nodes[0] == "gate_1_main"
    assert route.nodes[-1] == "platform_1_mid"

def test_accessible_path_avoids_stairs():
    # Route from Gate 1 to Platform 4 (must use lift or ramp, no stairs)
    route_acc = find_route_dijkstra_or_astar("gate_1_main", "platform_4_mid", accessible=True)
    assert route_acc.error is None
    assert route_acc.is_accessible is True
    
    # Verify no steps contain stairs
    for s in route_acc.steps:
        assert s.has_stairs is False or s.has_lift is True

def test_restricted_areas_excluded():
    G = load_station_graph("pune_junction")
    route = find_route_dijkstra_or_astar("platform_1_mid", "platform_2_mid", accessible=False, graph=G)
    assert route.error is None
    assert "track_1_2_restricted" not in route.nodes
