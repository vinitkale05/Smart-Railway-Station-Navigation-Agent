import os
import json
import time
import numpy as np
from typing import Dict, Any, List
from backend.agent.agent_loop import run_agent_loop
from backend.models.database import init_db
from backend.data.seed_data import seed_database
from backend.agent.guardrails import check_hallucination

def evaluate_test_set():
    seed_database()
    
    queries_path = os.path.join(os.path.dirname(__file__), "test_queries.json")
    with open(queries_path, "r", encoding="utf-8") as f:
        test_cases = json.load(f)
        
    total_queries = len(test_cases)
    tool_correct_count = 0
    routing_correct_count = 0
    hallucination_count = 0
    clarification_correct_count = 0
    clarification_cases_count = 0
    latencies_ms = []

    results_detail = []

    print(f"\n=======================================================")
    print(f"Starting Evaluation on {total_queries} Labeled Passenger Queries")
    print(f"=======================================================\n")

    for idx, tc in enumerate(test_cases, 1):
        session_id = f"eval_sess_{tc['id']}"
        t0 = time.time()
        resp = run_agent_loop(session_id, tc["query"])
        latency = (time.time() - t0) * 1000
        latencies_ms.append(latency)

        called_tools = [tc_item.get("tool") for tc_item in resp.tool_calls]
        expected_tools = tc.get("expected_tools", [])

        # 1. Tool Selection Accuracy
        tool_match = set(expected_tools).issubset(set(called_tools))
        if tool_match or (not expected_tools and resp.needs_clarification):
            tool_correct_count += 1

        # 2. Routing Accuracy
        routing_valid = True
        if "expected_platform" in tc:
            if not resp.route or resp.route.error:
                routing_valid = False
            else:
                target_plat_num = tc["expected_platform"].replace("Platform ", "")
                if not any(f"platform_{target_plat_num}" in n for n in resp.route.nodes):
                    routing_valid = False
            if tc.get("expected_accessible") and resp.route:
                if not resp.route.is_accessible:
                    routing_valid = False
            if routing_valid:
                routing_correct_count += 1
        elif "expected_facility_type" in tc:
            if resp.route and not resp.route.error:
                routing_correct_count += 1
        else:
            # Ambiguity or non-routing
            routing_correct_count += 1

        # 3. Hallucination Check
        grounded = check_hallucination(resp.text, resp.tool_calls)
        if not grounded:
            hallucination_count += 1

        # 4. Clarification Precision
        if tc.get("needs_clarification"):
            clarification_cases_count += 1
            if resp.needs_clarification:
                clarification_correct_count += 1
        elif resp.needs_clarification:
            clarification_cases_count += 1

        results_detail.append({
            "id": tc["id"],
            "query": tc["query"],
            "called_tools": called_tools,
            "latency_ms": round(latency, 2),
            "tool_match": tool_match,
            "hallucination": not grounded
        })

    tool_accuracy = (tool_correct_count / total_queries) * 100
    routing_accuracy = (routing_correct_count / total_queries) * 100
    hallucination_rate = (hallucination_count / total_queries) * 100
    clarification_precision = (clarification_correct_count / max(1, clarification_cases_count)) * 100
    p90_latency = float(np.percentile(latencies_ms, 90))
    avg_latency = float(np.mean(latencies_ms))

    report = {
        "total_test_queries": total_queries,
        "tool_selection_accuracy_percent": round(tool_accuracy, 2),
        "tool_selection_target": ">= 90%",
        "routing_accuracy_percent": round(routing_accuracy, 2),
        "routing_accuracy_target": ">= 95%",
        "hallucination_rate_percent": round(hallucination_rate, 2),
        "hallucination_rate_target": "0.0%",
        "clarification_precision_percent": round(clarification_precision, 2),
        "clarification_precision_target": ">= 85%",
        "p90_latency_ms": round(p90_latency, 2),
        "latency_target": "< 4000 ms",
        "average_latency_ms": round(avg_latency, 2),
        "all_metrics_passed": (
            tool_accuracy >= 90.0 and
            routing_accuracy >= 95.0 and
            hallucination_rate == 0.0 and
            clarification_precision >= 85.0 and
            p90_latency < 4000.0
        )
    }

    print(json.dumps(report, indent=2))
    
    # Save results to evaluation results file
    res_path = os.path.join(os.path.dirname(__file__), "evaluation_results.json")
    with open(res_path, "w", encoding="utf-8") as f:
        json.dump({"summary": report, "details": results_detail}, f, indent=2)

    return report

if __name__ == "__main__":
    evaluate_test_set()
