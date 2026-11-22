import networkx as nx
import math
from typing import Dict, Any, Optional
from backend.models.database import get_connection

def load_station_graph(station_id: str = "pune_junction") -> nx.Graph:
    """
    Constructs an undirected NetworkX graph from database nodes and edges.
    """
    conn = get_connection()
    c = conn.cursor()
    
    c.execute("SELECT * FROM nodes WHERE station_id = ?", (station_id,))
    nodes = c.fetchall()
    
    c.execute("""
        SELECT e.* FROM edges e 
        JOIN nodes n ON e.from_node = n.id 
        WHERE n.station_id = ?
    """, (station_id,))
    edges = c.fetchall()
    conn.close()
    
    G = nx.Graph()
    
    for n in nodes:
        G.add_node(
            n["id"],
            label=n["label"],
            type=n["type"],
            x=n["x"],
            y=n["y"],
            is_restricted=bool(n["is_restricted"])
        )
        
    for e in edges:
        G.add_edge(
            e["from_node"],
            e["to_node"],
            id=e["id"],
            distance_m=float(e["distance_m"]),
            has_stairs=bool(e["has_stairs"]),
            has_lift=bool(e["has_lift"]),
            is_step_free=bool(e["is_step_free"]),
            is_active=bool(e["is_active"])
        )
        
    return G
