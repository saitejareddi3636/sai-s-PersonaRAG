#!/usr/bin/env python3
from __future__ import annotations

import json
import statistics
import time
import urllib.error
import urllib.request
from pathlib import Path
import re

REPO = Path(__file__).resolve().parents[1]
QUESTIONS_PATH = REPO / "scripts" / "questions_50.txt"
OUT_JSON = REPO / "scripts" / "rag50_results.json"
API_URL = "http://localhost:8000/api/chat"

SOCIAL = {"hi", "hello", "hey there"}
HALLUCINATION_PATTERNS = [
    "university of california",
    "berkeley",
    "8 years",
]


def ask(question: str) -> tuple[dict, float, str | None]:
    payload = json.dumps({"question": question}).encode("utf-8")
    req = urllib.request.Request(
        API_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=40) as resp:
            raw = resp.read().decode("utf-8")
        dt = time.perf_counter() - t0
        return json.loads(raw), dt, None
    except urllib.error.URLError as e:
        dt = time.perf_counter() - t0
        return {}, dt, f"network_error: {e}"
    except Exception as e:
        dt = time.perf_counter() - t0
        return {}, dt, f"parse_error: {e}"


def evaluate(question: str, response: dict, dt: float, err: str | None) -> dict:
    answer = str(response.get("answer") or "").strip()
    confidence = str(response.get("confidence") or "unknown")
    sources = response.get("sources") or []
    sources_count = len(sources) if isinstance(sources, list) else 0

    failures: list[str] = []

    if err:
        failures.append(err)
    if len(answer) < 8:
        failures.append("short_or_empty")
    # Detect genuinely broken truncation like "I don" but allow valid refusals
    # such as "I don't have that information in my materials".
    if re.match(r"^i\s+don\s*$", answer.lower()):
        failures.append("truncated_answer")

    a_lower = answer.lower()
    for pat in HALLUCINATION_PATTERNS:
        if pat in a_lower:
            failures.append(f"hallucination_pattern:{pat}")

    if question.lower() not in SOCIAL and sources_count < 1:
        failures.append("no_sources")

    status = "PASS" if not failures else "FAIL"
    return {
        "question": question,
        "status": status,
        "latency_s": round(dt, 3),
        "confidence": confidence,
        "sources_count": sources_count,
        "answer": answer,
        "failures": failures,
    }


def main() -> None:
    questions = [
        line.strip()
        for line in QUESTIONS_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    results = []
    for i, q in enumerate(questions, start=1):
        response, dt, err = ask(q)
        row = evaluate(q, response, dt, err)
        row["index"] = i
        results.append(row)

    latencies = [r["latency_s"] for r in results]
    fails = [r for r in results if r["status"] == "FAIL"]

    summary = {
        "total": len(results),
        "pass": len(results) - len(fails),
        "fail": len(fails),
        "avg_latency_s": round(statistics.mean(latencies), 3) if latencies else 0.0,
        "p95_latency_s": sorted(latencies)[max(0, int(len(latencies) * 0.95) - 1)] if latencies else 0.0,
    }

    OUT_JSON.write_text(
        json.dumps({"summary": summary, "results": results}, indent=2),
        encoding="utf-8",
    )

    print("SUMMARY", json.dumps(summary))
    print("FAILURES", len(fails))
    for r in fails[:10]:
        print(
            f"- Q{r['index']}: {r['question']} | failures={','.join(r['failures'])} | ans={r['answer'][:140]}"
        )


if __name__ == "__main__":
    main()
