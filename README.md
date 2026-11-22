# Smart Railway Station Navigation Agent
### Final Year Major Project • Department of Computer Science and Engineering (AI)
**MIT-ADT University, Pune**

[![FastAPI / Starlette](https://img.shields.io/badge/Backend-FastAPI%20%2F%20Starlette-009688.svg)](https://fastapi.tiangolo.com)
[![NetworkX](https://img.shields.io/badge/Routing-NetworkX%20(A*%20%2F%20Dijkstra)-blue.svg)](https://networkx.org/)
[![React](https://img.shields.io/badge/Frontend-React%20%2B%20TypeScript-61DAFB.svg)](https://reactjs.org/)
[![WebSocket](https://img.shields.io/badge/RealTime-WebSockets-orange.svg)](https://websockets.readthedocs.io/)
[![WCAG 2.1 AA](https://img.shields.io/badge/Accessibility-WCAG%202.1%20AA-green.svg)](https://www.w3.org/WAI/standards-guidelines/wcag/)

---

## 🚂 Overview
The **Smart Railway Station Navigation Agent** is an agentic AI system engineered to guide passengers effortlessly through complex Indian railway stations from arrival to coach boarding. Modeled on **Pune Junction (PUNE)**, the agent accepts natural language voice and text queries, calculates shortest and step-free accessible routes, avoids staircases for wheelchairs and heavy luggage, locates nearby amenities (RO drinking water, accessible washrooms, food kiosks, cloak rooms), and automatically replans passenger routes with live push alerts whenever a last-minute platform change is published.

---

## 🌟 Key Features
- **Conversational Agent Loop:** Follows a rigorous Plan-Act-Observe-Respond cycle with multi-intent decomposition and a maximum 6-tool call turn cap.
- **Indoor Graph Routing ($A^*$ & Dijkstra):** Weighted undirected station graph with 65+ realistic nodes and 120+ edges.
- **Accessibility-Aware Guidance:** Step-free routes using lifts (L1-L4) and ramps, strictly avoiding stairs for senior citizens and wheelchairs.
- **Dynamic Platform Replanning:** Instantaneous recalculation of active passenger paths when platform changes or closures occur.
- **Real-Time WebSocket Dispatch:** Non-intrusive live alert banners and automated route updates pushed without page refresh.
- **Interactive SVG Station Map:** Clear 2D visualization of platforms 1-6, footbridges 1-2, lifts, stairs, restrooms, and pulsating passenger markers.
- **Turn-by-Turn Directions:** Step indicator with distance, walking ETA, "Mark Step as Completed" action, and Text-to-Speech audio readout.
- **Station Admin Console:** Protected management panel to publish platform reassignments and facility closures with live audit trails.
- **Comprehensive Evaluation Suite:** 65 labeled passenger test cases validating routing, tool calling, hallucination prevention, and sub-second latency.

---

## 🛠️ System Architecture

```
                          [ PASSENGER CLIENT ]
               (React / Responsive Web App / High Contrast)
                                   │
               ┌───────────────────┴───────────────────┐
               │ REST API (JSON)      WebSocket (/ws)  │
               ▼                                       ▼
    ┌────────────────────────────────────────────────────────┐
    │          FASTAPI / STARLETTE ASGI BACKEND ENGINE       │
    │  - Session Manager             - Pub-Sub Broadcast Hub │
    │  - Station / Train API         - Admin Auth (JWT)      │
    └────────────────────────────────────────────────────────┘
               │                                       ▲
               ▼                                       │
    ┌────────────────────────────────────────────────────────┐
    │                    AGENTIC AI LOOP                     │
    │  - Natural Language Intent Parser & Clarifier          │
    │  - Tool Registry & Execution Engine                    │
    │  - Guardrails (0% Hallucination, PNR Redaction)        │
    └────────────────────────────────────────────────────────┘
               │                                       │
               ▼                                       ▼
    ┌───────────────────────────┐   ┌────────────────────────┐
    │     ROUTING ENGINE        │   │    DATA PERSISTENCE    │
    │ - NetworkX Dijkstra & A*  │   │ - SQLite / PostgreSQL  │
    │ - Accessibility Filters   │   │ - Pune Junction Graph  │
    │ - Dynamic Replanner       │   │ - 40+ Synthetic Trains │
    └───────────────────────────┘   └────────────────────────┘
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+ installed
- Node.js 18+ (Optional; a pre-bundled modern SPA is served automatically by the backend for zero-install instant operation!)

### 2. Setup & Seeding
```bash
# Clone or navigate to the repository
cd "agentic ai"

# Install Python requirements
pip install -r requirements.txt

# Initialize & seed SQLite database with Pune Junction layout and trains
python3 -m backend.data.seed_data
```

### 3. Run the Backend & Application
```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```
Open your browser and navigate to:
👉 **`http://localhost:8000`**

---

## 🐳 Docker Deployment
To run with a single command via Docker Compose:
```bash
docker compose up --build
```
Access the application at `http://localhost:8000`.

---

## 🧪 Running Unit Tests & Evaluation Suite

### Run All Unit Tests (Pytest)
```bash
python3 -m pytest backend/tests/ -v
```

### Run Evaluation Suite (65 Labeled Test Queries)
```bash
python3 -m backend.evaluation.run_eval
```

**Evaluation Results Achieved:**
- **Routing Accuracy:** 96.92% *(Target: $\ge 95\%$)*
- **Tool Selection Accuracy:** 96.92% *(Target: $\ge 90\%$)*
- **Hallucination Rate:** 0.0% *(Target: $0.0\%$)*
- **Clarification Precision:** 100.0% *(Target: $\ge 85\%$)*
- **90th Percentile Latency:** 3.04 ms *(Target: $< 4000\text{ ms}$)*

---

## 📡 REST & WebSocket API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/sessions` | Create a passenger session with accessibility preferences |
| `POST` | `/api/sessions/{id}/messages` | Send passenger query to AI agent loop |
| `POST` | `/api/sessions/{id}/route` | Compute shortest / step-free path between two nodes |
| `POST` | `/api/sessions/{id}/step` | Advance navigation step and update current location |
| `GET` | `/api/stations` | List available stations |
| `GET` | `/api/stations/{id}/graph` | Return full node and edge coordinates for map rendering |
| `GET` | `/api/trains` | List all scheduled trains and current platform status |
| `GET` | `/api/trains/{train_no}` | Retrieve train schedule and platform info |
| `POST` | `/api/admin/login` | Authenticate station master / admin |
| `POST` | `/api/admin/platform-changes` | Publish platform change (triggers replanning & push) |
| `POST` | `/api/admin/closures` | Mark a lift or facility closed (triggers rerouting) |
| `WS` | `/ws/sessions/{id}` | Real-time WebSocket connection for live dispatch alerts |

---

## 📂 Project Directory Structure

```
agentic ai/
├── README.md                      # Project documentation and guide
├── requirements.txt               # Backend Python dependencies
├── docker-compose.yml             # Docker Compose orchestration
├── Dockerfile.backend             # Backend container definition
├── Dockerfile.frontend            # Frontend container definition
├── .env.example                   # Environment configuration template
├── docs/
│   ├── PRD_FINAL.md               # Finalized implementation PRD
│   └── PROJECT_REPORT.md          # Comprehensive academic project report
├── backend/
│   ├── main.py                    # Starlette/FastAPI application & routes
│   ├── config.py                  # Project settings & security configurations
│   ├── models/
│   │   ├── schemas.py             # Pydantic schemas (Nodes, Edges, Trains, Steps)
│   │   └── database.py            # SQLite database initialization & CRUD helpers
│   ├── data/
│   │   ├── pune_junction_graph.json  # 2D coordinates for Pune Junction layout
│   │   ├── synthetic_trains.json     # 40+ realistic Indian Railways trains
│   │   └── seed_data.py           # Database seeder script
│   ├── routing/
│   │   ├── graph_loader.py        # NetworkX station graph loader
│   │   ├── pathfinding.py         # Dijkstra and A* with accessibility filters
│   │   └── replanner.py           # Dynamic replanner on platform changes/closures
│   ├── tools/
│   │   ├── registry.py            # Tool definitions and dispatcher
│   │   └── implementations.py     # get_train_info, find_route, find_facility, etc.
│   ├── agent/
│   │   ├── prompts.py             # System prompts and instructions
│   │   ├── guardrails.py          # Hallucination checks & PNR sanitization
│   │   ├── fallback_engine.py     # Deterministic NLP agent engine
│   │   └── agent_loop.py          # Plan-Act-Observe-Respond orchestration
│   ├── events/
│   │   └── pubsub.py              # WebSocket connection and broadcast manager
│   ├── api/                       # API route handlers (stations, trains, sessions, admin)
│   ├── evaluation/
│   │   ├── test_queries.json      # 65 labeled test cases
│   │   └── run_eval.py            # Automated evaluation runner
│   └── tests/                     # 21 unit tests (routing, tools, agent, API)
└── frontend/
    ├── package.json               # Frontend dependencies
    ├── src/                       # React TypeScript modular source code
    └── static_spa/
        └── index.html             # Fully functional standalone interactive SPA
```

---

## 👥 Academic Credits
- **Course:** Final Year Major Project
- **Department:** Computer Science and Engineering (Artificial Intelligence)
- **Institution:** MIT-ADT University, Pune, Maharashtra, India
