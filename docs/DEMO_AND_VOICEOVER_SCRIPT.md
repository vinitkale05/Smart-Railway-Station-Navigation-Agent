# 🎬 Smart Railway Station Navigation Agent
## Comprehensive Project Demonstration & Voiceover Script

> **Project:** Smart Railway Station Navigation Agent (Final Year Major Project)  
> **Institution:** Department of Computer Science & Engineering, MIT-ADT University, Pune  
> **Deployment Site:** Pune Junction (PUNE), Central Railway  
> **Estimated Duration:** ~3 Minutes 45 Seconds  
> **Format:** Synchronized Screenplay with Visual Cues, Spoken Narration, Timing & Viva Defense  

---

## 🎙️ Voiceover Guidance & Speaker Notes

- **Voice Tone:** Professional, articulate, tech-savvy, and empathetic.
- **Pacing:** Moderate (~135-145 words per minute). Allow slight pauses `[PAUSE 1s]` during animations or UI transitions.
- **Pronunciation Notes:**
  - *Pune Junction:* `[POO-nay JUNK-shun]`
  - *FOB:* Speak as *"Foot Over Bridge"* (or *"F-O-B"*).
  - *Deccan Queen:* `[DEK-kən Queen]`
  - *NetworkX:* `[Network-Ex]`
  - *Dijkstra / A-Star:* `[DIKE-struh]` / `[A-Star]`
  - *WCAG:* `[WUH-cag two-point-one double-A]`

---

## ⏱️ Scene-by-Scene Demonstration Timeline

| Scene | Duration | Title & Key Focus | Core UI Action |
| :--- | :---: | :--- | :--- |
| **Scene 1** | 0:00 - 0:35 | Introduction & Problem Statement | Welcome screen, Pune Jn overview, accessibility toggle |
| **Scene 2** | 0:35 - 1:15 | Multi-Intent Gemini Agent & PNR Guardrails | Natural language chat, PNR redaction, step-free routing |
| **Scene 3** | 1:15 - 1:55 | Interactive Station Map & Zoom Navigation | Pan, Zoom-In (140%), stair avoidance path plotting |
| **Scene 4** | 1:55 - 2:40 | Real-Time Disruption & Live Alert Table | Admin platform change, right-side table update, live replan |
| **Scene 5** | 2:40 - 3:15 | Infrastructure Outage & Detour Routing | Marking broken lift, dynamic obstacle bypass, high contrast |
| **Scene 6** | 3:15 - 3:45 | Benchmark Results, Vercel Cloud & Conclusion | Evaluation metrics (0% hallucination), deployment, credits |

---

## 🎬 Synchronized Script (Action Cues + Voiceover)

---

### **Scene 1: Introduction & The Accessibility Problem**
**[0:00 - 0:35]**

#### 🖥️ Visual & Screen Action:
- Open application on `http://localhost:8000` (or Vercel production URL).
- The clean, accessible dashboard of Pune Junction is visible with the navigation bar, station badge `Pune Jn (PUNE)`, and the Welcome Modal.
- The cursor hovers over the **Require Step-Free / Accessible Route** checkbox and ticks it.
- Cursor highlights Gate 1 as the starting location and types `12124` for Deccan Queen.

#### 🗣️ Spoken Voiceover Narration:
> "Hello everyone. Welcome to the demonstration of our Final Year Major Project at MIT-ADT University: the **Smart Railway Station Navigation Agent**.
> 
> Major Indian railway stations like Pune Junction handle over two hundred thousand passengers daily across multiple platforms, foot-over-bridges, and facilities. For senior citizens, passengers with disabilities, or travellers carrying heavy luggage, navigating sudden platform changes and steep stairs is often chaotic, stressful, and physically demanding.
> 
> Our system bridges this gap by combining **Google Gemini Large Language Models**, deterministic **NetworkX Graph Algorithms**, and real-time **WebSocket event-driven replanning** to provide seamless, accessible, and 100% reliable indoor station navigation."

`[PAUSE 1.5s]`

---

### **Scene 2: Multi-Intent AI Agent & Privacy Guardrails**
**[0:35 - 1:15]**

#### 🖥️ Visual & Screen Action:
- Transition smoothly to the **Agent Chat** screen.
- Click a quick-prompt chip or type in the chat input:  
  `"My PNR is 8219482104. I am entering from Gate 1 with a wheelchair. Which platform is Train 12124 Deccan Queen, and how do I reach it safely?"`
- Press Enter.
- Show the subtle loading indicator and immediate response (< 300ms).
- Highlight on screen:
  1. The 10-digit PNR is automatically redacted to `[REDACTED PNR]` (Privacy compliance).
  2. The agent accurately retrieves Train 12124 arriving at Platform 1.
  3. The agent outputs accessible step-by-step turn-by-turn guidance explicitly utilizing ramps and Lift 1 while avoiding all stairs.

#### 🗣️ Spoken Voiceover Narration:
> "Let’s start as a passenger entering Pune Junction from Gate 1. In the chat, the user inputs their query along with a 10-digit PNR number, requesting wheelchair-accessible navigation to the famous Deccan Queen, Train 12124.
> 
> Notice two critical engineering guardrails here:
> First, our privacy middleware immediately redacts sensitive PNR data before external processing.
> Second, to guarantee zero hallucination, the agent does not invent directions. Instead, it delegates routing to an internal topological graph engine using Euclidean $A^*$ search.
> 
> Because the user requested wheelchair accessibility, the agent strictly penalizes and eliminates all 5 station staircases, guiding the passenger through Concourse Ramp 1, North Foot-Over-Bridge, and Lift 1 straight to Platform 1."

`[PAUSE 1.5s]`

---

### **Scene 3: Interactive Station Map & Zoom Navigation**
**[1:15 - 1:55]**

#### 🖥️ Visual & Screen Action:
- Click the **Navigation Map** tab in the header or the *"View on Interactive Map"* button in the chat.
- Show the Pune Junction vector SVG map rendering all 6 platforms, North & Central FOBs, Waiting Halls, Food Courts, and Lifts.
- Click the **Zoom In (+)** button twice to zoom to 140%.
- Drag and pan the map to show the highlighted blue path traversing from `gate_1_main` $\rightarrow$ `concourse_ramp_1` $\rightarrow$ `lift_1_fob_north` $\rightarrow$ `platform_1_mid`.
- Click the **Reset (100%)** button to restore full station view.
- Hover over restricted track areas to show they are locked and inaccessible to passenger routing.

#### 🗣️ Spoken Voiceover Narration:
> "Switching to the Interactive Station Map, we see an exact spatial representation of Pune Junction's 6 platforms, connected via North and Central Foot-Over-Bridges.
> 
> Passengers can seamlessly zoom in and out using interactive controls or mouse-wheel gestures, and drag to pan across the station.
> 
> Notice how the active route is plotted in vibrant blue. The algorithm selected the North FOB Lift because it provides an unbroken step-free trajectory. Yellow restricted nodes mark railway operational tracks—our spatial engine guarantees passengers are never routed across dangerous open tracks."

`[PAUSE 1.5s]`

---

### **Scene 4: Real-Time Platform Disruption & Decoupled Alert Table**
**[1:55 - 2:40]**

#### 🖥️ Visual & Screen Action:
- Open the **Admin** panel (or trigger via split view).
- Log into Admin (demo credentials `station_admin` / `admin123`).
- Under **Publish Platform Change**, select Train `12124 (Deccan Queen)` and change platform from `Platform 1` to `Platform 3` with reason *"Incoming rake delayed / track congestion"*.
- Click **"Publish Live Platform Change"**.
- Switch instantly back to **Agent Chat**.
- Highlight the **Right-Hand Side Live Alert Table**:
  - The alert appears cleanly inside the dedicated **Platform Changes** tab with a red badge count `1`.
  - The alert is decoupled from passenger conversational text so the passenger's chat history remains clean and uncluttered.
- Notice the agent simultaneously triggers **Auto-Replanning**:
  - A real-time notification sounds.
  - The route recalculates automatically: now directing the passenger across Central FOB via Lift 3 to Platform 3.

#### 🗣️ Spoken Voiceover Narration:
> "Now, let’s test the system under real-world railway chaos: an emergency platform change.
> 
> In the Station Master Admin console, the controller discovers track congestion and switches Train 12124 from Platform 1 to Platform 3.
> 
> Instantly, via low-latency WebSockets, two things occur:
> On the right side of the Agent Chat, our dedicated **Live Alert Table** registers the disruption with zero interference to the passenger's conversation stream.
> Simultaneously, our event-driven replanning engine detects that the active session's destination has changed. In under 3 milliseconds, it calculates a new accessible detour—rerouting the passenger safely via Central FOB Lift 3 down to Platform 3, without requiring the user to re-ask or panic."

`[PAUSE 1.5s]`

---

### **Scene 5: Infrastructure Outage & Accessible Detours**
**[2:40 - 3:15]**

#### 🖥️ Visual & Screen Action:
- In the Admin panel, go to **Mark Lift / Facility Closure**.
- Select `lift_1_fob_north (North FOB Lift 1)`, status `maintenance`, reason *"Periodic maintenance & cable overhaul"*.
- Click **"Publish Infrastructure Closure"**.
- In the Agent chat, the right-side alert table switches to the **Lift/Facility Closures** tab, showing Lift 1 marked with an amber badge `Out of Service`.
- Click the **High Contrast Mode** toggle in the top bar (`fa-circle-half-stroke`) to demonstrate WCAG 2.1 AA high-contrast dark yellow/black theme for visually impaired users.

#### 🗣️ Spoken Voiceover Narration:
> "What happens if a lift breaks down? Let’s find out.
> 
> The station controller marks North FOB Lift 1 as out of service.
> In our graph topology, that node’s weight is immediately set to infinity. The navigation agent dynamically routes any incoming wheelchair passenger through Central FOB Lift 3, ensuring no traveller ever arrives at a broken lift.
> 
> Furthermore, with one click, users can toggle **High Contrast Mode**, engineered specifically to comply with WCAG 2.1 AA accessibility guidelines for low-vision and visually impaired passengers."

`[PAUSE 1.5s]`

---

### **Scene 6: Evaluation Benchmarks, Cloud Deployment & Conclusion**
**[3:15 - 3:45]**

#### 🖥️ Visual & Screen Action:
- Show terminal or evaluation report summary from `backend/evaluation/run_eval.py`:
  - 65 test queries passed.
  - Routing Accuracy: 96.92%.
  - Hallucination Rate: **0.0%**.
  - P90 Latency: **2.95 ms**.
- Show the live Vercel deployment and GitHub repository `vinitkale05/Smart-Railway-Station-Navigation-Agent`.
- Fade to conclusion slide with MIT-ADT University Pune academic credits.

#### 🗣️ Spoken Voiceover Narration:
> "To validate our system, we benchmarked the agent across 65 multi-intent synthetic queries simulating complex passenger journeys, ambiguous requests, and facility queries.
> 
> The results speak for themselves:
> - **Zero percent hallucination rate** achieved through strict tool-grounded reasoning.
> - **96.9% routing and tool invocation accuracy**.
> - And a sub-3 millisecond P90 pathfinding latency.
> 
> The entire project is containerized, Vercel-ready with serverless ASGI support, and open-sourced on GitHub.
> 
> This concludes our demonstration of the Smart Railway Station Navigation Agent. Thank you!"

---

## 🎓 Viva Voce / External Examiner Defense Q&A

Here are the top technical questions examiners ask during project presentations, with model answers:

### Q1: Why use an LLM (Gemini) with NetworkX rather than letting the LLM generate routes directly?
> **Answer:** Large Language Models are probabilistic and prone to hallucination. Generating spatial coordinates or navigation paths directly with an LLM leads to illegal turns, stairs recommended to wheelchair users, or walking across active tracks. We used Gemini strictly as a natural language semantic reasoning agent that invokes deterministic, mathematically proven graph algorithms ($A^*$ with Euclidean heuristic on NetworkX). This architecture guarantees 100% spatial safety and a 0.0% hallucination rate.

### Q2: How does the system handle real-time replanning at scale?
> **Answer:** We implemented an event-driven publish-subscribe architecture. When an admin publishes a platform reassignment or closure, the backend replanner checks all active in-memory session states. If a passenger's target train or path traverses an affected node, a non-blocking background task recomputes the route in under 3 milliseconds and pushes the updated path via WebSockets (with polling fallback for serverless environments).

### Q3: How is passenger privacy protected?
> **Answer:** We implemented regex-based PNR sanitization and PII redaction middleware prior to sending prompts to the Gemini API. Even if a passenger types their 10-digit ticket number, mobile number, or name, it is redacted locally to prevent identity leakage.

### Q4: How is the application deployed on Vercel if Vercel serverless doesn't support persistent WebSockets?
> **Answer:** We engineered a hybrid communication architecture. The backend runs as a serverless ASGI application via `@vercel/python` in `api/index.py` with SQLite mounted to `/tmp`. On the client side, if WebSocket connections are closed or unavailable, the SPA automatically transitions to lightweight HTTP polling every 4 seconds, ensuring 100% feature parity.
