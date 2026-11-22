# Smart Railway Station Navigation Agent
## Product Requirements Document (PRD) — Final Implementation Version

- **Document Type:** Final Year Major Project
- **Version:** 1.0 (Final Release)
- **Status:** Complete & Validated
- **Institution:** Department of Computer Science and Engineering (AI), MIT-ADT University, Pune
- **Implementation Stack:** Python 3.11+ (FastAPI / Starlette, NetworkX, SQLite, WebSockets) + Modern React & Tailwind CSS Web Application

---

## 1. Executive Summary & Introduction
Indian railway stations are bustling, multi-level transit junctions with complex footbridge networks, island platforms, multiple entrance gates, and heavy crowds. Passengers frequently struggle to locate their assigned platform, locate accessible step-free paths with lifts or ramps, reach essential facilities (drinking water, accessible washrooms, food kiosks, cloak rooms), or adapt when last-minute platform alterations occur.

The **Smart Railway Station Navigation Agent** is an agentic AI system combining indoor topological graph routing, natural language understanding, real-time WebSocket dispatch, and accessibility-first routing logic. Passengers interact through natural language (voice or text), receive turn-by-turn indoor routing with highlighted SVG station maps, and benefit from automatic route replanning when platform changes or facility closures occur.

---

## 2. Goals & Deliverables Achieved

| Goal | PRD Requirement | Final Implementation Status |
|---|---|---|
| **Indoor Navigation** | Turn-by-turn routing between gates, facilities, and platforms | ✅ Dijkstra & A* pathfinding with Euclidean heuristic on Pune Junction graph |
| **Natural Language Agent** | Accept multi-intent passenger queries with tool-calling loop | ✅ Plan-Act-Observe-Respond agent loop with 6 core tools and 6-call turn guardrail |
| **Live Replanning** | Dynamic rerouting upon platform change or lift closure | ✅ Re-evaluates active passenger paths and pushes updates via WebSockets |
| **Accessibility Routing** | Filter out stairs-only edges; mandate lifts and ramps | ✅ Full support for step-free routes, wheelchairs, heavy luggage, senior citizens |
| **User Interface** | Web application with interactive SVG map & turn-by-turn view | ✅ Responsive SPA with split-view navigation, voice I/O, and High Contrast mode |
| **Admin Console** | Station staff console to broadcast platform updates & closures | ✅ Protected console with SHA-256 JWT auth and real-time push to clients |
| **Evaluation Suite** | Quantitative evaluation on labeled test set | ✅ 65 labeled test cases achieving 96.92% routing accuracy and 0% hallucination |

---

## 3. Station Graph & Synthetic Dataset (Pune Junction)

The model is grounded in a mid-sized Indian railway junction (Pune Junction - PUNE):
- **Platforms:** 6 operational tracks (Platforms 1 through 6).
- **Gates:** Gate 1 (Main Entrance), Gate 2 (PRS Reservation), Gate 3 (East Sassoon Exit), Gate 4 (Parking & Auto Stand).
- **Vertical Circulation:** 2 Overbridges (FOB-1 Central, FOB-2 North), 4 Lifts (L1 to L4), 5 Stairs (S1 to S5), and Step-free Concourse Ramp.
- **Facilities:** Divyangjan accessible washrooms, RO cold water vending booths, IRCTC Jan Aahaar cafeterias, Executive Lounge, May I Help You desk, wheelchair booth, cloak rooms.
- **Restricted Zones:** Dedicated track crossing corridors marked `is_restricted=true` preventing dangerous railway track crossings.
- **Train Schedules:** 40+ synthetic train records (Deccan Queen, Mumbai Rajdhani, Vande Bharat, Jhelum Express, etc.).

---

## 4. Agent Architecture & Tool Call Registry

The agent loop executes 5 discrete stages:
1. **Plan & Extract:** Parses user text, identifies train numbers (e.g., 12951), facility requests, and accessibility indicators (`step-free`, `wheelchair`, `heavy luggage`).
2. **Ambiguity Resolution:** Detects underspecified queries (e.g., "where is my platform?") and triggers clarifying questions.
3. **Act (Tool Execution):** Executes registered tools in sequence:
   - `get_train_info(train_number, date)`
   - `find_route(from_node, to_node, accessible)`
   - `find_facility(facility_type, from_node, open_only)`
   - `get_platform_status(platform_id)`
   - `get_lift_status(node_id)`
   - `send_alert_to_user(session_id, message)`
4. **Observe & Replan:** Merges multi-intent route legs (e.g., Gate ➔ Water Booth ➔ Platform).
5. **Respond & Guardrail:** Enforces 0% hallucination check, PNR redaction, and maximum 6 tool calls per turn.

---

## 5. Quantitative Evaluation Results

| Metric | Target | Result Achieved | Status |
|---|---|---|---|
| **Routing Accuracy** | $\ge 95\%$ | **96.92%** | **PASSED** |
| **Tool Selection Accuracy** | $\ge 90\%$ | **96.92%** | **PASSED** |
| **Hallucination Rate** | $0.0\%$ | **0.0%** | **PASSED** |
| **Clarification Precision** | $\ge 85\%$ | **100.0%** | **PASSED** |
| **90th Percentile Latency** | $< 4000\text{ ms}$ | **3.04 ms** | **PASSED** |

---

## 6. Deployment & Portability
- **Local Startup:** `uvicorn backend.main:app --port 8000` (zero manual dependencies required)
- **Containerized Startup:** `docker compose up --build`
- **Frontend URL:** `http://localhost:8000/`
