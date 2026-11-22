import os
import json
from datetime import datetime
from backend.models.database import get_connection, init_db

def seed_database():
    init_db()
    conn = get_connection()
    c = conn.cursor()
    
    # 1. Load Station Graph
    graph_path = os.path.join(os.path.dirname(__file__), "pune_junction_graph.json")
    with open(graph_path, "r", encoding="utf-8") as f:
        graph_data = json.load(f)
        
    st = graph_data["station"]
    c.execute("INSERT OR REPLACE INTO stations (id, name, city, timezone) VALUES (?, ?, ?, ?)",
              (st["id"], st["name"], st["city"], st["timezone"]))
              
    for node in graph_data["nodes"]:
        c.execute("""
        INSERT OR REPLACE INTO nodes (id, station_id, type, label, x, y, is_restricted, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            node["id"],
            node["station_id"],
            node["type"],
            node["label"],
            node["x"],
            node["y"],
            1 if node.get("is_restricted", False) else 0,
            json.dumps(node.get("metadata", {}))
        ))
        
    for edge in graph_data["edges"]:
        c.execute("""
        INSERT OR REPLACE INTO edges (id, from_node, to_node, distance_m, has_stairs, has_lift, is_step_free, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            edge["id"],
            edge["from_node"],
            edge["to_node"],
            edge["distance_m"],
            1 if edge.get("has_stairs") else 0,
            1 if edge.get("has_lift") else 0,
            1 if edge.get("is_step_free", True) else 0,
            1 if edge.get("is_active", True) else 0
        ))
        
    # 2. Load Trains
    trains_path = os.path.join(os.path.dirname(__file__), "synthetic_trains.json")
    with open(trains_path, "r", encoding="utf-8") as f:
        trains_data = json.load(f)
        
    now_str = datetime.now().isoformat()
    for tr in trains_data:
        c.execute("""
        INSERT OR REPLACE INTO trains (train_no, name, origin, destination, scheduled_departure, default_platform, current_platform, delay_minutes, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            tr["train_no"],
            tr["name"],
            tr["origin"],
            tr["destination"],
            tr["scheduled_departure"],
            tr["default_platform"],
            tr["default_platform"],
            0,
            "On Time"
        ))
        
        # Add initial platform assignment
        # Map platform string to node_id
        plat_num = tr["default_platform"].replace("Platform ", "").strip()
        p_node_id = f"platform_{plat_num}_mid"
        c.execute("""
        INSERT INTO platform_assignments (train_no, platform_node_id, effective_from, source, delay_minutes)
        VALUES (?, ?, ?, ?, ?)
        """, (
            tr["train_no"],
            p_node_id,
            now_str,
            "schedule",
            0
        ))
        
    # 3. Load Facilities
    facilities = [
        {"id": "fac_wash_main", "node_id": "washroom_concourse", "facility_type": "washroom", "name": "Concourse Divyangjan & General Restrooms", "is_accessible": True, "opening_hours": "24x7"},
        {"id": "fac_wash_p23", "node_id": "washroom_p2_3", "facility_type": "washroom", "name": "Platform 2/3 Restrooms", "is_accessible": True, "opening_hours": "24x7"},
        {"id": "fac_wash_p45", "node_id": "washroom_p4_5", "facility_type": "washroom", "name": "Platform 4/5 Restrooms", "is_accessible": False, "opening_hours": "24x7"},
        
        {"id": "fac_water_main", "node_id": "water_concourse", "facility_type": "water", "name": "RO Cold Drinking Water Booth (Concourse)", "is_accessible": True, "opening_hours": "24x7"},
        {"id": "fac_water_p23", "node_id": "water_p2_3", "facility_type": "water", "name": "Drinking Water Fountain P2/3", "is_accessible": True, "opening_hours": "24x7"},
        {"id": "fac_water_p45", "node_id": "water_p4_5", "facility_type": "water", "name": "Drinking Water Vending Machine P4/5", "is_accessible": True, "opening_hours": "24x7"},
        
        {"id": "fac_food_janaahaar", "node_id": "food_jan_aahaar", "facility_type": "food", "name": "IRCTC Jan Aahaar Cafeteria", "is_accessible": True, "opening_hours": "05:00 - 23:30"},
        {"id": "fac_food_chai", "node_id": "food_chai_p2_3", "facility_type": "food", "name": "Chai & Snack Kiosk (P2/3)", "is_accessible": True, "opening_hours": "24x7"},
        {"id": "fac_food_book", "node_id": "food_bookstall_p4_5", "facility_type": "food", "name": "Wheeler Snacks & Refreshments (P4/5)", "is_accessible": True, "opening_hours": "06:00 - 23:00"},
        
        {"id": "fac_wait_exec", "node_id": "waiting_executive", "facility_type": "waiting_room", "name": "IRCTC AC Executive Lounge", "is_accessible": True, "opening_hours": "24x7"},
        {"id": "fac_wait_ladies", "node_id": "waiting_ladies", "facility_type": "waiting_room", "name": "Ladies Waiting Room", "is_accessible": True, "opening_hours": "24x7"},
        {"id": "fac_wait_gen", "node_id": "waiting_general", "facility_type": "waiting_room", "name": "General Passenger Waiting Hall", "is_accessible": True, "opening_hours": "24x7"},
        
        {"id": "fac_help_desk", "node_id": "help_desk_main", "facility_type": "help_desk", "name": "May I Help You & Tourist Assistance", "is_accessible": True, "opening_hours": "24x7"},
        {"id": "fac_wheelchair", "node_id": "wheelchair_booth", "facility_type": "help_desk", "name": "Divyangjan Wheelchair Assistance Booth", "is_accessible": True, "opening_hours": "24x7"},
        {"id": "fac_cloak", "node_id": "cloak_room", "facility_type": "cloak_room", "name": "Cloak Room & Luggage Locker", "is_accessible": True, "opening_hours": "24x7"},
        {"id": "fac_ticket", "node_id": "ticket_counter_general", "facility_type": "ticket_counter", "name": "General Ticket Booking & Automatic Ticket Vending Machines (ATVM)", "is_accessible": True, "opening_hours": "24x7"}
    ]
    
    for fac in facilities:
        c.execute("""
        INSERT OR REPLACE INTO facilities (id, node_id, facility_type, name, is_open, opening_hours, is_accessible)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            fac["id"],
            fac["node_id"],
            fac["facility_type"],
            fac["name"],
            1,
            fac["opening_hours"],
            1 if fac["is_accessible"] else 0
        ))
        
    conn.commit()
    conn.close()
    print("Database successfully seeded with station layout, trains, and facilities!")

if __name__ == "__main__":
    seed_database()
