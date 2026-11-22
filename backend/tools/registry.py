from typing import Dict, Any, Callable
from backend.tools.implementations import (
    get_train_info,
    find_route,
    find_facility,
    get_platform_status,
    get_lift_status,
    send_alert_to_user
)

TOOL_DEFINITIONS = [
    {
        "name": "get_train_info",
        "description": "Get scheduled platform, departure time, and delay for an Indian Railways train by its train number.",
        "parameters": {
            "type": "object",
            "properties": {
                "train_number": {
                    "type": "string",
                    "description": "5-digit train number (e.g., '12951', '12124', '22224')."
                },
                "date": {
                    "type": "string",
                    "description": "Optional travel date in YYYY-MM-DD format."
                }
            },
            "required": ["train_number"]
        }
    },
    {
        "name": "find_route",
        "description": "Calculate the shortest walking path or step-free accessible path between two station locations.",
        "parameters": {
            "type": "object",
            "properties": {
                "from_node": {
                    "type": "string",
                    "description": "Starting node ID, e.g. 'gate_1_main', 'concourse_main', 'platform_1_mid'."
                },
                "to_node": {
                    "type": "string",
                    "description": "Destination node ID, e.g. 'platform_4_mid', 'washroom_concourse', 'waiting_executive'."
                },
                "accessible": {
                    "type": "boolean",
                    "description": "Set to true to mandate step-free/lift routes avoiding stairs-only paths."
                }
            },
            "required": ["from_node", "to_node"]
        }
    },
    {
        "name": "find_facility",
        "description": "Find the nearest facility of a specified type (washroom, water, food, waiting_room, help_desk, ticket_counter, cloak_room) sorted by walking distance.",
        "parameters": {
            "type": "object",
            "properties": {
                "facility_type": {
                    "type": "string",
                    "description": "Category of facility: 'washroom', 'water', 'food', 'waiting_room', 'help_desk', 'ticket_counter', 'cloak_room'."
                },
                "from_node": {
                    "type": "string",
                    "description": "Current user location node ID (default 'gate_1_main')."
                },
                "open_only": {
                    "type": "boolean",
                    "description": "Whether to return only currently open facilities (default true)."
                }
            },
            "required": ["facility_type"]
        }
    },
    {
        "name": "get_platform_status",
        "description": "Get current trains and status for a specific railway platform (e.g. 'Platform 1', 'Platform 4').",
        "parameters": {
            "type": "object",
            "properties": {
                "platform_id": {
                    "type": "string",
                    "description": "Platform identifier, e.g. 'Platform 1', 'Platform 3', 'Platform 4'."
                }
            },
            "required": ["platform_id"]
        }
    },
    {
        "name": "get_lift_status",
        "description": "Check whether a lift or vertical elevator node is operational or under maintenance.",
        "parameters": {
            "type": "object",
            "properties": {
                "node_id": {
                    "type": "string",
                    "description": "Node identifier for the lift (e.g. 'lift_l1_p1', 'lift_l2_p2_3', 'lift_l3_p4_5', 'lift_l4_p6')."
                }
            },
            "required": ["node_id"]
        }
    },
    {
        "name": "send_alert_to_user",
        "description": "Send a high-priority advisory or platform-change notification to a passenger's active session.",
        "parameters": {
            "type": "object",
            "properties": {
                "session_id": {
                    "type": "string",
                    "description": "The active session ID."
                },
                "message": {
                    "type": "string",
                    "description": "The alert message text to display."
                }
            },
            "required": ["session_id", "message"]
        }
    }
]

TOOL_MAP: Dict[str, Callable] = {
    "get_train_info": get_train_info,
    "find_route": find_route,
    "find_facility": find_facility,
    "get_platform_status": get_platform_status,
    "get_lift_status": get_lift_status,
    "send_alert_to_user": send_alert_to_user
}

def execute_tool_call(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    if tool_name not in TOOL_MAP:
        return {"error": f"Unknown tool: {tool_name}"}
    func = TOOL_MAP[tool_name]
    try:
        return func(**arguments)
    except Exception as e:
        return {"error": f"Tool execution failed for '{tool_name}': {str(e)}"}
