"""
eval/eval_runner.py

Runs golden dataset against the agent. Scores:
  (a) tool routing accuracy
  (b) groundedness (faq answers only) — reply contains key phrase from reference_answer
  (c) relevancy — LLM-as-judge 1-5 score via Groq
  (d) latency per query
  (e) token count from Groq response

Usage:
    python -m eval.eval_runner
"""

import json
import os
import time
import sys

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# Import agent internals — scorer runs in-process, no server needed
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.agent import run_agent, client as groq_client
from app.memory import conversation_memory

GOLDEN_PATH = os.path.join(os.path.dirname(__file__), "golden.json")


def detect_tool_called(session_id: str, question: str) -> tuple[str, str, float, int]:
    """
    Run agent, detect which tool was actually called, return
    (tool_called, reply, latency_ms, tokens_used).

    Patch: wrap run_agent and intercept tool routing by checking reply source.
    Simpler: re-run with sentinel detection on raw LLM output — but that requires
    touching agent internals. Instead, infer from reply content post-hoc:
      - reply starts with "Order ORD-" or "No order found" → order_tool
      - reply looks like FAQ chunk text → faq_tool
      - otherwise → none

    This is imperfect for edge cases but good enough for 105 golden cases
    without modifying agent.py.
    """
    # Clear memory for this session so each eval question is independent
    conversation_memory.pop(session_id, None)

    start = time.perf_counter()

    # Monkey-patch Groq client to capture token usage
    original_create = groq_client.chat.completions.create
    captured = {}

    def patched_create(*args, **kwargs):
        resp = original_create(*args, **kwargs)
        captured["usage"] = resp.usage
        return resp

    groq_client.chat.completions.create = patched_create
    try:
        reply = run_agent(session_id, question)
    finally:
        groq_client.chat.completions.create = original_create

    latency_ms = (time.perf_counter() - start) * 1000
    tokens = captured.get("usage").total_tokens if captured.get("usage") else 0

    # Infer tool called from reply shape
    if reply.startswith("Order ORD-") or reply.startswith("No order found"):
        tool_called = "order_tool"
    else:
        # Check if reply text overlaps significantly with FAQ content
        # (FAQ tool returns raw chunk text, not a sentence constructed by LLM)
        faq_keywords = [
            "return", "refund", "ship", "deliver", "payment", "cancel",
            "exchange", "promo", "invoice", "credit", "tracking", "account",
            "password", "damaged", "defective", "cod", "gst", "warehouse"
        ]
        reply_lower = reply.lower()
        faq_hit = any(kw in reply_lower for kw in faq_keywords)

        # If agent politely declined (out-of-scope), it won't hit faq keywords heavily
        # Heuristic: if reply contains "only assist" or "store-related" → none
        decline_phrases = ["only assist", "store-related", "help you with store", "not able to help with that"]
        is_decline = any(p in reply_lower for p in decline_phrases)

        if is_decline:
            tool_called = "none"
        elif faq_hit:
            tool_called = "faq_tool"
        else:
            tool_called = "none"

    return tool_called, reply, latency_ms, tokens


def score_groundedness(reply: str, reference_answer: str) -> bool:
    """
    Groundedness: check if any key phrase from reference_answer appears in reply.
    Splits reference into clauses, checks if at least one clause is present.
    """
    if not reference_answer:
        return True  # N/A for order_tool and none cases

    clauses = [c.strip().lower() for c in reference_answer.split(".") if c.strip()]
    reply_lower = reply.lower()
    return any(clause[:30] in reply_lower for clause in clauses if len(clause) > 10)


def score_relevancy_llm(question: str, reply: str) -> int:
    """
    LLM-as-judge: ask Groq to score reply relevancy 1-5.
    Returns int score. On failure returns 0.
    """
    prompt = (
        f"Question: {question}\n"
        f"Reply: {reply}\n\n"
        "Rate how relevant and helpful this reply is to the question on a scale of 1 to 5. "
        "1 = completely irrelevant, 5 = perfectly relevant and helpful. "
        "Reply with a single integer only."
    )
    try:
        resp = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=5,
        )
        return int(resp.choices[0].message.content.strip()[0])
    except Exception:
        return 0


def run_eval(llm_judge: bool = True) -> dict:
    with open(GOLDEN_PATH) as f:
        golden = json.load(f)

    results = []
    total = len(golden)

    print(f"Running eval on {total} questions...")

    for i, item in enumerate(golden, 1):
        session_id = f"eval-{item['id']}"
        question = item["question"]
        expected_tool = item["expected_tool"]
        reference_answer = item.get("reference_answer")

        tool_called, reply, latency_ms, tokens = detect_tool_called(session_id, question)

        routing_correct = tool_called == expected_tool
        grounded = score_groundedness(reply, reference_answer) if expected_tool == "faq_tool" else None
        relevancy = score_relevancy_llm(question, reply) if llm_judge else None

        results.append({
            "id": item["id"],
            "question": question,
            "expected_tool": expected_tool,
            "tool_called": tool_called,
            "routing_correct": routing_correct,
            "grounded": grounded,
            "relevancy_score": relevancy,
            "latency_ms": round(latency_ms, 1),
            "tokens_used": tokens,
            "reply": reply,
        })

        status = "✓" if routing_correct else "✗"
        print(f"[{i}/{total}] {status} id={item['id']} tool={tool_called} latency={latency_ms:.0f}ms")

    # Aggregate metrics
    routing_correct_count = sum(1 for r in results if r["routing_correct"])
    routing_accuracy = routing_correct_count / total * 100

    faq_results = [r for r in results if r["expected_tool"] == "faq_tool"]
    grounded_count = sum(1 for r in faq_results if r["grounded"] is True)
    hallucination_rate = (1 - grounded_count / len(faq_results)) * 100 if faq_results else 0

    avg_latency = sum(r["latency_ms"] for r in results) / total
    avg_tokens = sum(r["tokens_used"] for r in results) / total
    # Groq llama-3.1-8b-instant: ~$0.05 per 1M tokens
    cost_per_100 = (avg_tokens * 100 * 0.05) / 1_000_000

    relevancy_scores = [r["relevancy_score"] for r in results if r["relevancy_score"] is not None]
    avg_relevancy = sum(relevancy_scores) / len(relevancy_scores) if relevancy_scores else None

    summary = {
        "total_questions": total,
        "routing_accuracy_pct": round(routing_accuracy, 2),
        "hallucination_rate_pct": round(hallucination_rate, 2),
        "avg_latency_ms": round(avg_latency, 1),
        "avg_tokens_per_query": round(avg_tokens, 1),
        "estimated_cost_per_100_queries_usd": round(cost_per_100, 5),
        "avg_relevancy_score": round(avg_relevancy, 2) if avg_relevancy else None,
    }

    return {"summary": summary, "results": results}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--no-llm-judge", action="store_true", help="Skip LLM-as-judge scoring (faster, cheaper)")
    args = parser.parse_args()

    report = run_eval(llm_judge=not args.no_llm_judge)

    out_dir = os.path.join(os.path.dirname(__file__))
    os.makedirs(out_dir, exist_ok=True)

    json_path = os.path.join(out_dir, "report.json")
    with open(json_path, "w") as f:
        json.dump(report, f, indent=2)

    # Markdown summary table
    s = report["summary"]
    md = f"""# Eval Report

| Metric | Value |
|---|---|
| Total questions | {s['total_questions']} |
| Tool routing accuracy | {s['routing_accuracy_pct']}% |
| Hallucination rate (FAQ) | {s['hallucination_rate_pct']}% |
| Avg latency | {s['avg_latency_ms']} ms |
| Avg tokens/query | {s['avg_tokens_per_query']} |
| Est. cost per 100 queries | ${s['estimated_cost_per_100_queries_usd']} |
| Avg relevancy score (1-5) | {s['avg_relevancy_score'] or 'N/A'} |

## Failures

| ID | Question | Expected | Got |
|---|---|---|---|
"""
    failures = [r for r in report["results"] if not r["routing_correct"]]
    for r in failures:
        md += f"| {r['id']} | {r['question'][:60]} | {r['expected_tool']} | {r['tool_called']} |\n"

    md_path = os.path.join(out_dir, "report.md")
    with open(md_path, "w") as f:
        f.write(md)

    print("\n=== SUMMARY ===")
    for k, v in s.items():
        print(f"  {k}: {v}")
    print(f"\nreport.json → {json_path}")
    print(f"report.md   → {md_path}")