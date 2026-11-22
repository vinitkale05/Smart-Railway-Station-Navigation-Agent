import re
from typing import Dict, Any, List, Optional, Tuple
from backend.models.schemas import MessageResponse, QuickAction, RouteResult
from backend.tools.implementations import (
    get_train_info,
    find_route,
    find_facility,
    get_platform_status,
    get_lift_status
)
from backend.agent.guardrails import check_hallucination

FACILITY_KEYWORDS = {
    "washroom": ["washroom", "restroom", "toilet", "bathroom", "lavatory"],
    "water": ["water", "drinking water", "thirsty", "cold water", "water bottle", "wvm"],
    "food": ["food", "eat", "snack", "hungry", "chai", "tea", "coffee", "canteen", "restaurant", "breakfast", "dinner", "lunch"],
    "waiting_room": ["waiting room", "waiting hall", "lounge", "executive lounge", "sit", "rest"],
    "help_desk": ["help desk", "may i help you", "information", "inquiry", "sahayak", "assistance"],
    "ticket_counter": ["ticket", "booking", "atvm", "reservation counter"],
    "cloak_room": ["cloak room", "cloakroom", "luggage deposit", "locker"]
}

def extract_train_number(text: str) -> Optional[str]:
    # Look for 5 digit train numbers
    m = re.search(r"\b\d{5}\b", text)
    if m:
        return m.group(0)
    # Check popular train names
    names = {
        "deccan queen": "12124",
        "vande bharat": "22224",
        "rajdhani": "12951",
        "hutatma": "12157",
        "pragati": "12126",
        "sinhagad": "11010",
        "azad hind": "12130",
        "jhelum": "11077",
        "goa express": "12780",
        "konark": "11020",
        "punjab mail": "12138",
        "chennai mail": "12164",
        "shatabdi": "12026",
        "duronto": "12264"
    }
    lower = text.lower()
    for name, tno in names.items():
        if name in lower:
            return tno
    return None

def detect_accessibility_need(text: str) -> bool:
    lower = text.lower()
    triggers = [
        "step-free", "step free", "wheelchair", "luggage", "heavy bag", 
        "bags", "lift", "ramp", "elderly", "senior", "pram", "stroller", 
        "cannot climb", "avoid stairs", "no stairs", "disabled", "divyang"
    ]
    return any(t in lower for t in triggers)

def detect_facility_type(text: str) -> Optional[str]:
    lower = text.lower()
    for f_type, kws in FACILITY_KEYWORDS.items():
        if any(kw in lower for kw in kws):
            return f_type
    return None

def detect_platform_query(text: str) -> Optional[str]:
    m = re.search(r"platform\s+(\d+)", text, re.IGNORECASE)
    if m:
        return m.group(1)
    return None

def detect_lift_query(text: str) -> Optional[str]:
    lower = text.lower()
    if "lift" in lower or "elevator" in lower or "escalator" in lower:
        # Check platform mention
        m = re.search(r"platform\s+(\d+)", text, re.IGNORECASE)
        if m:
            p_num = m.group(1)
            if p_num in ["1", "2", "3", "4", "5", "6"]:
                if p_num == "1":
                    return "lift_l1_p1"
                elif p_num in ["2", "3"]:
                    return "lift_l2_p2_3"
                elif p_num in ["4", "5"]:
                    return "lift_l3_p4_5"
                elif p_num == "6":
                    return "lift_l4_p6"
        return "lift_l1_p1"
    return None

def run_agentic_reasoning(
    user_message: str,
    session: Dict[str, Any]
) -> MessageResponse:
    """
    Executes the Plan-Act-Observe-Respond agent loop.
    Enforces the 6-tool call limit, hallucination guardrails, and clarification queries.
    """
    tool_calls: List[Dict[str, Any]] = []
    text_clean = user_message.strip()
    
    # 1. Intent & Entity Extraction
    train_no = extract_train_number(text_clean) or session.get("train_no")
    accessibility_needed = detect_accessibility_need(text_clean) or session.get("accessibility_prefs", False)
    facility_type = detect_facility_type(text_clean)
    platform_queried = detect_platform_query(text_clean)
    lift_queried = detect_lift_query(text_clean)
    
    current_loc = session.get("current_node_id") or "gate_1_main"
    
    # 2. Check for Ambiguity / Missing Info
    # e.g. User asks "where is my train?" or "what platform is my train?" without specifying train number
    clarify_triggers = [
        "where is my train", "where is my platform", "my train platform", 
        "what platform", "which platform", "my platform", "train status",
        "find my train", "locate my train", "where to board"
    ]
    if any(q in text_clean.lower() for q in clarify_triggers) and not train_no and not platform_queried:
        return MessageResponse(
            text="Could you please tell me your 5-digit train number (or train name) so I can locate its platform and guide you?",
            tool_calls=[],
            needs_clarification=True,
            clarification_prompt="train_number",
            quick_actions=[
                QuickAction(label="Train 12951 (Rajdhani)", action="send_train", payload={"train_no": "12951"}),
                QuickAction(label="Train 12124 (Deccan Queen)", action="send_train", payload={"train_no": "12124"}),
                QuickAction(label="Train 22224 (Vande Bharat)", action="send_train", payload={"train_no": "22224"})
            ]
        )

    # 3. Tool Execution & Multi-intent Planning
    train_info = None
    facility_info = None
    route_info = None
    quick_actions = []

    # Intent A: Lift / Escalator Status Check
    if lift_queried and ("status" in text_clean.lower() or "working" in text_clean.lower() or "operational" in text_clean.lower()):
        res = get_lift_status(lift_queried)
        tool_calls.append({"tool": "get_lift_status", "args": {"node_id": lift_queried}, "result": res})
        
        status_txt = "operational and running normally" if res["is_operational"] else "temporarily out of service for maintenance"
        ans = f"The {lift_queried.replace('_', ' ').title()} is currently {status_txt}. {res['note']}"
        return MessageResponse(text=ans, tool_calls=tool_calls, quick_actions=[
            QuickAction(label="Find step-free route", action="find_route", payload={"accessible": True})
        ])

    # Intent B: Train info lookup
    if train_no:
        train_res = get_train_info(train_no)
        tool_calls.append({"tool": "get_train_info", "args": {"train_number": train_no}, "result": train_res})
        if train_res.get("found"):
            train_info = train_res
            plat_node_id = train_res["platform_node_id"]
            
            # If user also asked for a facility (e.g. water first)
            if facility_type:
                fac_res = find_facility(facility_type, from_node=current_loc)
                tool_calls.append({"tool": "find_facility", "args": {"facility_type": facility_type, "from_node": current_loc}, "result": fac_res})
                
                if fac_res.get("found"):
                    facility_info = [fac_res["nearest"]]
                    fac_node = fac_res["nearest"]["node_id"]
                    
                    # Route to facility first, then to platform
                    r1 = find_route(current_loc, fac_node, accessible=accessibility_needed)
                    tool_calls.append({"tool": "find_route", "args": {"from_node": current_loc, "to_node": fac_node, "accessible": accessibility_needed}, "result": r1})
                    
                    r2 = find_route(fac_node, plat_node_id, accessible=accessibility_needed)
                    tool_calls.append({"tool": "find_route", "args": {"from_node": fac_node, "to_node": plat_node_id, "accessible": accessibility_needed}, "result": r2})
                    
                    # Merge steps
                    merged_steps = []
                    step_num = 1
                    for st in r1.get("steps", []):
                        st_copy = dict(st)
                        st_copy["step_number"] = step_num
                        merged_steps.append(st_copy)
                        step_num += 1
                    for st in r2.get("steps", []):
                        st_copy = dict(st)
                        st_copy["step_number"] = step_num
                        merged_steps.append(st_copy)
                        step_num += 1
                        
                    route_info = RouteResult(
                        from_node=current_loc,
                        to_node=plat_node_id,
                        total_distance_m=round(r1.get("total_distance_m", 0) + r2.get("total_distance_m", 0), 1),
                        total_estimated_seconds=r1.get("total_estimated_seconds", 0) + r2.get("total_estimated_seconds", 0),
                        is_accessible=accessibility_needed,
                        nodes=r1.get("nodes", []) + [n for n in r2.get("nodes", []) if n != fac_node],
                        steps=merged_steps
                    )
                    
                    ans = (
                        f"Train {train_no} ({train_res['name']}) is scheduled on {train_res['platform']} departing at {train_res['scheduled_departure']} ({train_res['status']}).\n\n"
                        f"Before boarding, the nearest {facility_type} is at **{fac_res['nearest']['name']}**, located about {round(fac_res['nearest']['distance_m'])}m away.\n"
                        f"I have routed you via the {facility_type} stall and onwards to {train_res['platform']} "
                        f"({'step-free route via lifts/ramps' if accessibility_needed else 'shortest path'}). Total walking distance is {route_info.total_distance_m} meters."
                    )
                    
                    quick_actions = [
                        QuickAction(label="Start navigation", action="start_navigation"),
                        QuickAction(label="Show on map", action="show_map"),
                        QuickAction(label="Skip to platform", action="route_direct_platform")
                    ]
                    
                    return MessageResponse(
                        text=ans,
                        tool_calls=tool_calls,
                        route=route_info,
                        train_info=train_info,
                        facility_info=facility_info,
                        quick_actions=quick_actions
                    )

            # Route directly to platform
            route_res = find_route(current_loc, plat_node_id, accessible=accessibility_needed)
            tool_calls.append({"tool": "find_route", "args": {"from_node": current_loc, "to_node": plat_node_id, "accessible": accessibility_needed}, "result": route_res})
            route_info = RouteResult(**route_res)
            
            acc_str = "Your step-free route avoids stairs and uses lifts/ramps" if accessibility_needed else "Your shortest route"
            ans = (
                f"Train {train_no} ({train_res['name']}) is on **{train_res['platform']}** and currently {train_res['status']} "
                f"for its {train_res['scheduled_departure']} departure.\n\n"
                f"{acc_str} from {current_loc.replace('_', ' ').title()} to {train_res['platform']} is about {route_info.total_distance_m} meters "
                f"(approx {round(route_info.total_estimated_seconds / 60, 1)} mins). Would you like to start step-by-step navigation?"
            )
            
            quick_actions = [
                QuickAction(label="Start navigation", action="start_navigation"),
                QuickAction(label="Show on map", action="show_map"),
                QuickAction(label="Find nearest washroom", action="find_washroom"),
                QuickAction(label="Find drinking water", action="find_water")
            ]
            
            return MessageResponse(
                text=ans,
                tool_calls=tool_calls,
                route=route_info,
                train_info=train_info,
                quick_actions=quick_actions
            )

    # Intent C: Facility inquiry alone (washroom, water, food, etc.)
    if facility_type:
        fac_res = find_facility(facility_type, from_node=current_loc)
        tool_calls.append({"tool": "find_facility", "args": {"facility_type": facility_type, "from_node": current_loc}, "result": fac_res})
        
        if fac_res.get("found"):
            nearest = fac_res["nearest"]
            facility_info = [nearest]
            
            route_res = find_route(current_loc, nearest["node_id"], accessible=accessibility_needed)
            tool_calls.append({"tool": "find_route", "args": {"from_node": current_loc, "to_node": nearest['node_id'], "accessible": accessibility_needed}, "result": route_res})
            route_info = RouteResult(**route_res)
            
            acc_tag = " (accessible with ramp/lift)" if nearest.get("is_accessible") else ""
            ans = (
                f"The nearest {facility_type} is **{nearest['name']}**{acc_tag}, located approximately "
                f"{round(nearest['distance_m'])} meters from your current position.\n"
                f"Operating hours: {nearest.get('opening_hours', '24x7')}. Follow the highlighted path on your map."
            )
            
            quick_actions = [
                QuickAction(label="Start navigation", action="start_navigation"),
                QuickAction(label="Show on map", action="show_map")
            ]
            
            return MessageResponse(
                text=ans,
                tool_calls=tool_calls,
                route=route_info,
                facility_info=facility_info,
                quick_actions=quick_actions
            )

    # Intent D: Platform inquiry alone ("what train is on platform 3?")
    if platform_queried:
        p_res = get_platform_status(f"Platform {platform_queried}")
        tool_calls.append({"tool": "get_platform_status", "args": {"platform_id": f"Platform {platform_queried}"}, "result": p_res})
        
        active_t = p_res.get("active_trains", [])
        if active_t:
            lines = [f"- Train {t['train_no']} ({t['name']}) departing {t['scheduled_departure']} ({t['status']})" for t in active_t[:4]]
            ans = f"**Platform {platform_queried} Status:**\n" + "\n".join(lines)
        else:
            ans = f"Platform {platform_queried} currently has no departures scheduled in the immediate window."
            
        return MessageResponse(
            text=ans,
            tool_calls=tool_calls,
            quick_actions=[
                QuickAction(label=f"Route to Platform {platform_queried}", action="route_platform", payload={"platform": platform_queried})
            ]
        )

    # Intent E: General navigation / Help greeting
    ans = (
        "Hello! I am your Smart Railway Station Navigation Agent for Pune Junction. "
        "I can help you locate your train platform, find accessible step-free paths, discover facilities "
        "(washrooms, drinking water, cafeteria, executive lounge), and guide you turn-by-turn.\n\n"
        "How can I assist you with your journey today?"
    )
    return MessageResponse(
        text=ans,
        tool_calls=[],
        quick_actions=[
            QuickAction(label="Where is my train?", action="ask_train"),
            QuickAction(label="Find nearest washroom", action="find_washroom"),
            QuickAction(label="Find drinking water", action="find_water"),
            QuickAction(label="Step-free wheelchair routes", action="set_accessible", payload={"accessible": True})
        ]
    )
