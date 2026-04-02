"""
Knowledge Capsule System

Based on arXiv:2601.03220 "From Entropy to Epiplexity".

Every completed task creates a reusable "capability capsule" -- a distilled
piece of knowledge that makes future similar tasks easier and more reliable.

Capsules are stored in a flat JSON file (data/capsules.json) so the system
stays self-contained and easy to inspect.

Integration points:
  - After AcademicTask completes + passes audit -> extract_capsule()
  - Before dispatching a new task -> find_matching_capsule() -> apply_capsule()
"""

from __future__ import annotations

import json
import logging
import math
import os
import re
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Resolve default storage path relative to *this* file's package root.
_DEFAULT_CAPSULE_PATH = str(
    Path(__file__).resolve().parent.parent / "data" / "capsules.json"
)


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class CapabilityCapsule:
    """A reusable piece of knowledge extracted from a successful task."""

    capsule_id: str
    task_type: str
    description: str
    code_template: str
    parameters: Dict
    success_conditions: str
    epiplexity_score: float
    times_used: int
    success_rate: float
    created_from_task: str
    created_at: str  # ISO-8601 string for JSON round-tripping

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "CapabilityCapsule":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


# ---------------------------------------------------------------------------
# Persistence helpers (JSON file)
# ---------------------------------------------------------------------------

def _load_capsules(path: str) -> List[Dict]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _save_capsules(capsules: List[Dict], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(capsules, fh, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Core engine
# ---------------------------------------------------------------------------

class KnowledgeEngine:
    """Extracts, stores, and reuses capability capsules."""

    def __init__(self, capsule_path: Optional[str] = None) -> None:
        self._path = capsule_path or _DEFAULT_CAPSULE_PATH

    # ------------------------------------------------------------------
    # Extract
    # ------------------------------------------------------------------

    def extract_capsule(
        self,
        task_id: str,
        task_type: str,
        description: str,
        code: str,
        output: str,
        parameters: Optional[Dict] = None,
        success_conditions: str = "",
    ) -> Optional[CapabilityCapsule]:
        """Create a capsule from a successfully completed task.

        Returns ``None`` when the code is too trivial to warrant a capsule
        (fewer than 3 non-blank lines).
        """
        stripped_lines = [ln for ln in code.splitlines() if ln.strip()]
        if len(stripped_lines) < 3:
            logger.debug("Code too short to extract a capsule (<%d lines)", 3)
            return None

        epiplexity = self.calculate_epiplexity(code, output)
        template = self._distill_template(code)

        capsule = CapabilityCapsule(
            capsule_id=uuid.uuid4().hex[:12],
            task_type=task_type,
            description=description,
            code_template=template,
            parameters=parameters or {},
            success_conditions=success_conditions,
            epiplexity_score=round(epiplexity, 4),
            times_used=0,
            success_rate=0.0,
            created_from_task=task_id,
            created_at=datetime.now(timezone.utc).isoformat(),
        )

        self._persist(capsule)
        logger.info(
            "Extracted capsule %s from task %s (epiplexity=%.4f)",
            capsule.capsule_id,
            task_id,
            epiplexity,
        )
        return capsule

    # ------------------------------------------------------------------
    # Find
    # ------------------------------------------------------------------

    def find_matching_capsule(
        self,
        description: str,
        task_type: str,
    ) -> Optional[CapabilityCapsule]:
        """Return the best matching capsule for a new task.

        Scoring:
          - Same task_type is required.
          - Description similarity via SequenceMatcher (0-1).
          - Weighted by success_rate and epiplexity_score.
        """
        all_caps = _load_capsules(self._path)
        candidates = [c for c in all_caps if c.get("task_type") == task_type]
        if not candidates:
            return None

        best_score = -1.0
        best_capsule: Optional[Dict] = None

        for cap in candidates:
            sim = SequenceMatcher(
                None,
                description.lower(),
                cap.get("description", "").lower(),
            ).ratio()

            sr = cap.get("success_rate", 0.0)
            ep = cap.get("epiplexity_score", 0.0)

            # Combined score: similarity dominates, boosted by quality signals.
            score = sim * 0.6 + sr * 0.25 + ep * 0.15
            if score > best_score:
                best_score = score
                best_capsule = cap

        if best_capsule is None or best_score < 0.15:
            return None

        logger.info(
            "Matched capsule %s (score=%.3f) for '%s'",
            best_capsule.get("capsule_id"),
            best_score,
            description[:60],
        )
        return CapabilityCapsule.from_dict(best_capsule)

    # ------------------------------------------------------------------
    # Apply
    # ------------------------------------------------------------------

    def apply_capsule(
        self,
        capsule: CapabilityCapsule,
        new_task: Dict,
    ) -> str:
        """Inject capsule knowledge into a task prompt.

        Returns an enhanced prompt string that a downstream LLM can use.
        """
        parts: List[str] = []
        parts.append(f"## Prior Knowledge (capsule {capsule.capsule_id})")
        parts.append("")
        parts.append(f"A similar task ({capsule.task_type}) was solved before.")
        parts.append(f"Description: {capsule.description}")
        if capsule.success_conditions:
            parts.append(f"Success conditions: {capsule.success_conditions}")
        parts.append("")
        parts.append("### Reusable code template")
        parts.append("```python")
        parts.append(capsule.code_template)
        parts.append("```")
        if capsule.parameters:
            parts.append("")
            parts.append("### Known-good parameters")
            for key, val in capsule.parameters.items():
                parts.append(f"- {key}: {val}")
        parts.append("")
        parts.append("### New task")
        parts.append(f"Description: {new_task.get('description', '')}")
        if new_task.get("parameters"):
            parts.append(f"Parameters: {json.dumps(new_task['parameters'])}")
        parts.append("")
        parts.append(
            "Adapt the template above to the new task. "
            "Keep what works, change what differs."
        )
        return "\n".join(parts)

    # ------------------------------------------------------------------
    # Record reuse outcome
    # ------------------------------------------------------------------

    def record_reuse(self, capsule_id: str, success: bool) -> None:
        """Update ``times_used`` and ``success_rate`` after a capsule is reused."""
        all_caps = _load_capsules(self._path)
        for cap in all_caps:
            if cap.get("capsule_id") == capsule_id:
                prev_used = cap.get("times_used", 0)
                prev_rate = cap.get("success_rate", 0.0)
                new_used = prev_used + 1
                new_rate = (prev_rate * prev_used + (1.0 if success else 0.0)) / new_used
                cap["times_used"] = new_used
                cap["success_rate"] = round(new_rate, 4)
                break
        _save_capsules(all_caps, self._path)

    # ------------------------------------------------------------------
    # Epiplexity calculation
    # ------------------------------------------------------------------

    def calculate_epiplexity(self, code: str, output: str) -> float:
        """Epiplexity = structural_complexity - time_bounded_entropy.

        structural_complexity
            Approximated from code length, unique callable names, and
            branching depth.

        time_bounded_entropy
            Approximated from the ratio of unique tokens in the output
            to total tokens (normalised randomness proxy).

        The result is clamped to [0, 1].
        """
        sc = self._structural_complexity(code)
        tbe = self._time_bounded_entropy(output)
        raw = sc - tbe
        return max(0.0, min(1.0, raw))

    # ------------------------------------------------------------------
    # Agent / platform expertise summary
    # ------------------------------------------------------------------

    def get_agent_expertise(self, agent_id: Optional[str] = None) -> Dict:
        """Summarise expertise from stored capsules.

        If *agent_id* is ``None``, returns platform-wide statistics.

        Returns::

            {
                task_type: {
                    "capsules": int,
                    "avg_success": float,
                    "expertise_level": str,   # novice / competent / expert
                }
            }
        """
        all_caps = _load_capsules(self._path)

        buckets: Dict[str, List[Dict]] = {}
        for cap in all_caps:
            tt = cap.get("task_type", "unknown")
            buckets.setdefault(tt, []).append(cap)

        result: Dict[str, Dict] = {}
        for tt, caps in buckets.items():
            n = len(caps)
            avg_sr = sum(c.get("success_rate", 0.0) for c in caps) / n if n else 0.0
            if n >= 10 and avg_sr >= 0.8:
                level = "expert"
            elif n >= 3 and avg_sr >= 0.5:
                level = "competent"
            else:
                level = "novice"
            result[tt] = {
                "capsules": n,
                "avg_success": round(avg_sr, 3),
                "expertise_level": level,
            }

        return result

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _persist(self, capsule: CapabilityCapsule) -> None:
        all_caps = _load_capsules(self._path)
        all_caps.append(capsule.to_dict())
        _save_capsules(all_caps, self._path)

    @staticmethod
    def _distill_template(code: str) -> str:
        """Strip overly specific literals and inline comments to produce a
        reusable skeleton.
        """
        lines: List[str] = []
        for line in code.splitlines():
            cleaned = re.sub(r"#.*$", "", line).rstrip()
            if cleaned.strip():
                lines.append(cleaned)
        return "\n".join(lines)

    @staticmethod
    def _structural_complexity(code: str) -> float:
        """Heuristic structural complexity in [0, 1]."""
        lines = [ln for ln in code.splitlines() if ln.strip()]
        num_lines = len(lines)
        if num_lines == 0:
            return 0.0

        # Unique callable names (def / class)
        callables = set(re.findall(r"\bdef\s+(\w+)", code))
        callables |= set(re.findall(r"\bclass\s+(\w+)", code))

        # Max indentation depth as a branching proxy
        max_indent = 0
        for ln in lines:
            stripped = ln.lstrip()
            indent = len(ln) - len(stripped)
            max_indent = max(max_indent, indent)

        length_factor = min(1.0, num_lines / 200.0)
        callable_factor = min(1.0, len(callables) / 15.0)
        branch_factor = min(1.0, max_indent / 20.0)

        raw = length_factor * 0.4 + callable_factor * 0.35 + branch_factor * 0.25
        return max(0.0, min(1.0, raw))

    @staticmethod
    def _time_bounded_entropy(output: str) -> float:
        """Heuristic randomness measure of output in [0, 1]."""
        tokens = re.findall(r"\S+", output)
        if not tokens:
            return 0.0
        unique = set(tokens)
        ratio = len(unique) / len(tokens)
        # Scale so that a fully unique token stream maps to ~0.5 (moderate
        # entropy), leaving room for truly noisy outputs.
        return min(1.0, ratio * 0.6)
