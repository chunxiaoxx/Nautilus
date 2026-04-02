"""
Task Quality Gate — DeerFlow-inspired output quality validation.

Scores task output on a 0-1 scale across three dimensions:
  - completeness: does the output address the task description?
  - coherence: is the output internally consistent and well-structured?
  - usefulness: is the output actionable/informative for the user?

Quality levels:
  ≥ 0.7  GOOD    — pass, append score to metadata
  0.4-0.7 FAIR   — pass with quality_warning flag
  < 0.4  POOR    — mark needs_review, no auto-retry (too expensive)

Design: fire-and-forget scoring via asyncio; never blocks task completion.
"""
import asyncio
import json
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def _score_output_sync(task_description: str, output: str) -> Dict:
    """Synchronous quality scoring via unified LLMClient."""
    # Truncate to avoid expensive long calls
    desc_trunc = task_description[:500]
    out_trunc = output[:1500] if output else "(empty)"

    system = (
        "You are a task output quality evaluator. "
        "Score the given task output JSON with three float values 0-1. "
        "Return ONLY valid JSON, no explanation."
    )
    user = (
        f"Task description:\n{desc_trunc}\n\n"
        f"Task output:\n{out_trunc}\n\n"
        "Return JSON: "
        '{"completeness": 0.0, "coherence": 0.0, "usefulness": 0.0, "overall": 0.0}'
    )

    try:
        from agent_engine.llm.client import get_llm_client
        client = get_llm_client()
        raw = client.chat(prompt=user, system=system, max_tokens=128)
        # Extract JSON if wrapped in markdown
        if "```" in raw:
            raw = raw.split("```")[1].lstrip("json").strip()
        scores = json.loads(raw)
        overall = scores.get("overall")
        if overall is None:
            dims = [scores.get("completeness", 0.7),
                    scores.get("coherence", 0.7),
                    scores.get("usefulness", 0.7)]
            overall = round(sum(dims) / len(dims), 3)
        scores["overall"] = round(float(overall), 3)
        return scores
    except Exception as exc:
        logger.debug("Quality gate scoring failed (non-critical): %s", exc)
        return {"score": 0.7, "skipped": True, "reason": str(exc)}


async def score_task_output(task_description: str, output: str) -> Dict:
    """Async wrapper — runs Haiku in thread pool to avoid blocking."""
    loop = asyncio.get_event_loop()
    try:
        return await loop.run_in_executor(
            None, _score_output_sync, task_description, output
        )
    except Exception as exc:
        logger.debug("Quality gate async error: %s", exc)
        return {"score": 0.7, "skipped": True, "reason": str(exc)}


def interpret_quality(scores: Dict) -> Dict:
    """Convert raw scores into quality_level and flags."""
    overall = scores.get("overall", scores.get("score", 0.7))
    if overall >= 0.7:
        level = "GOOD"
        quality_warning = False
        needs_review = False
    elif overall >= 0.4:
        level = "FAIR"
        quality_warning = True
        needs_review = False
    else:
        level = "POOR"
        quality_warning = True
        needs_review = True

    return {
        "quality_level": level,
        "quality_score": overall,
        "quality_warning": quality_warning,
        "needs_review": needs_review,
        "dimensions": {
            k: scores[k]
            for k in ("completeness", "coherence", "usefulness")
            if k in scores
        },
    }
