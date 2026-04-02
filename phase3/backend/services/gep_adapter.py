"""
GEP Protocol Adapter - Connects Nautilus to EvoMap global evolution network.

Implements the Genome Evolution Protocol (GEP) to enable:
- Publishing Nautilus agent capabilities as Genes/Capsules to EvoMap
- Fetching proven solutions from the EvoMap marketplace
- Reporting execution results back to the network

GEP Protocol: https://evomap.ai/blog/gep-protocol-deep-dive
No API key required - agents POST to https://evomap.ai/a2a/hello
"""
import os
import hashlib
import logging
import time
from typing import Optional
from datetime import datetime

import httpx

logger = logging.getLogger(__name__)

EVOMAP_HUB_URL = os.getenv("EVOMAP_HUB_URL", "https://evomap.ai")
NAUTILUS_NODE_ID = os.getenv("NAUTILUS_NODE_ID", "nautilus-core-v1")


class GEPAdapter:
    """Adapter between Nautilus internal formats and GEP protocol."""

    def __init__(self, hub_url: str = EVOMAP_HUB_URL, node_id: str = NAUTILUS_NODE_ID):
        self._hub_url = hub_url.rstrip("/")
        self._node_id = node_id
        self._registered = False

    async def hello(self) -> dict:
        """Register with the EvoMap hub (GEP hello message)."""
        envelope = _gep_envelope("hello", {
            "node_id": self._node_id,
            "capabilities": ["code_execution", "data_labeling", "scientific_computing"],
            "version": "1.0.0",
            "platform": "nautilus",
        })
        result = await self._post("/a2a/hello", envelope)
        self._registered = result.get("success", False)
        logger.info(f"EvoMap hello: registered={self._registered}")
        return result

    async def publish_gene(
        self,
        name: str,
        description: str,
        code: str,
        task_type: str,
        confidence: float = 0.8,
        tags: Optional[list] = None,
    ) -> dict:
        """
        Publish a reusable strategy (Gene) to EvoMap.

        A Gene is a proven solution template that other agents can discover
        and reuse. Generated from successful task completions.
        """
        gene_id = _content_hash(code)
        envelope = _gep_envelope("publish", {
            "asset_type": "gene",
            "asset_id": gene_id,
            "name": name,
            "description": description,
            "code": code,
            "task_type": task_type,
            "confidence": confidence,
            "tags": tags or [],
            "origin_node": self._node_id,
        })
        result = await self._post("/a2a/publish", envelope)
        logger.info(f"Published gene {gene_id}: {name}")
        return {"gene_id": gene_id, **result}

    async def publish_capsule(
        self,
        name: str,
        trigger_signal: str,
        fix_code: str,
        validation_command: str,
        confidence: float = 0.9,
        environment: Optional[dict] = None,
    ) -> dict:
        """
        Publish a validated fix (Capsule) to EvoMap.

        A Capsule is a validated fix bundled with trigger signals,
        confidence scores, and environment fingerprints.
        """
        capsule_id = _content_hash(fix_code + trigger_signal)
        envelope = _gep_envelope("publish", {
            "asset_type": "capsule",
            "asset_id": capsule_id,
            "name": name,
            "trigger_signal": trigger_signal,
            "fix_code": fix_code,
            "validation_command": validation_command,
            "confidence": confidence,
            "environment": environment or {},
            "origin_node": self._node_id,
        })
        result = await self._post("/a2a/publish", envelope)
        logger.info(f"Published capsule {capsule_id}: {name}")
        return {"capsule_id": capsule_id, **result}

    async def fetch_solutions(
        self,
        query: str,
        task_type: Optional[str] = None,
        limit: int = 5,
    ) -> list:
        """
        Fetch proven solutions from EvoMap for a given problem.

        Returns a list of Genes/Capsules ranked by GDI score.
        """
        envelope = _gep_envelope("fetch", {
            "query": query,
            "task_type": task_type,
            "limit": limit,
            "requester_node": self._node_id,
        })
        result = await self._post("/a2a/fetch", envelope)
        assets = result.get("assets", [])
        logger.info(f"Fetched {len(assets)} solutions for: {query[:50]}")
        return assets

    async def report_result(
        self,
        asset_id: str,
        success: bool,
        execution_time: float,
        notes: str = "",
    ) -> dict:
        """
        Report execution result of a Gene/Capsule back to EvoMap.

        This feeds into the GDI (Global Desirability Index) scoring.
        """
        envelope = _gep_envelope("report", {
            "asset_id": asset_id,
            "success": success,
            "execution_time": execution_time,
            "notes": notes,
            "reporter_node": self._node_id,
        })
        return await self._post("/a2a/report", envelope)

    async def _post(self, path: str, data: dict) -> dict:
        """Send a GEP message to the hub."""
        url = f"{self._hub_url}{path}"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=data)
                if response.status_code == 200:
                    return response.json()
                logger.warning(f"EvoMap {path} returned {response.status_code}")
                return {"success": False, "status": response.status_code}
        except httpx.ConnectError:
            logger.warning(f"EvoMap hub not reachable: {url}")
            return {"success": False, "error": "hub_unreachable"}
        except Exception as e:
            logger.error(f"EvoMap request failed: {e}")
            return {"success": False, "error": str(e)}


def _gep_envelope(msg_type: str, payload: dict) -> dict:
    """Create a GEP protocol envelope."""
    return {
        "protocol": "gep",
        "version": "1.0",
        "type": msg_type,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "payload": payload,
    }


def _content_hash(content: str) -> str:
    """SHA-256 content-addressable ID (GEP standard)."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


# Singleton
_adapter: Optional[GEPAdapter] = None


def get_gep_adapter() -> GEPAdapter:
    """Get the global GEP adapter instance."""
    global _adapter
    if _adapter is None:
        _adapter = GEPAdapter()
    return _adapter
