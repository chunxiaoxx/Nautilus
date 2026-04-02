"""
Memory Hierarchy - Working/Short-term/Long-term with importance decay.

Extends the existing AgentMemorySystem with a 3-tier architecture:
- WORKING: Current task context (Redis/in-memory cache, 5min TTL)
- SHORT_TERM: Recent experiences (PostgreSQL, 30-day decay)
- LONG_TERM: Core knowledge (PostgreSQL + vector index, permanent)
"""
import json
import logging
import uuid
from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel

logger = logging.getLogger(__name__)

WORKING_TTL_SECONDS = 300
SHORT_TERM_MAX_AGE_DAYS = 30
PROMOTION_THRESHOLD = 0.8
PROMOTION_MIN_AGE_DAYS = 7
DECAY_RATE_PER_WEEK = 0.05
CLEANUP_MIN_IMPORTANCE = 0.1
SIMILARITY_WEIGHT = 0.6
IMPORTANCE_WEIGHT = 0.4


class MemoryTier(str, Enum):
    WORKING = "working"
    SHORT_TERM = "short"
    LONG_TERM = "long"


class MemoryEntry(BaseModel):
    memory_id: str
    content: str
    tier: MemoryTier
    importance: float
    agent_id: int
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None
    similarity: Optional[float] = None


class MemoryHierarchy:
    """3-tier memory system for agents: working, short-term, long-term."""

    def __init__(self, agent_id: int, db_pool: Any) -> None:
        self._agent_id = agent_id
        self._db_pool = db_pool
        self._embedding_service: Any = None
        self._cache: Any = None

    @property
    def embeddings(self) -> Any:
        if self._embedding_service is None:
            from memory.embedding_service import get_embedding_service
            self._embedding_service = get_embedding_service()
        return self._embedding_service

    @property
    def cache(self) -> Any:
        if self._cache is None:
            from utils.cache import get_cache
            self._cache = get_cache()
        return self._cache

    def _working_key(self, memory_id: str) -> str:
        return f"mem:working:{self._agent_id}:{memory_id}"

    def _working_index_key(self) -> str:
        return f"mem:working_idx:{self._agent_id}"

    async def store(self, content: str, tier: MemoryTier = MemoryTier.SHORT_TERM,
                    importance: float = 0.5,
                    metadata: Optional[Dict[str, Any]] = None) -> str:
        """Store a memory in the specified tier. Returns memory_id."""
        importance = max(0.0, min(1.0, importance))
        memory_id = str(uuid.uuid4())
        if tier == MemoryTier.WORKING:
            return await self._store_working(memory_id, content, importance, metadata)
        return await self._store_persistent(memory_id, content, tier, importance, metadata)

    async def _store_working(self, memory_id: str, content: str,
                             importance: float,
                             metadata: Optional[Dict[str, Any]]) -> str:
        """Store in working memory (cache with TTL)."""
        entry = {
            "memory_id": memory_id, "content": content,
            "importance": importance, "agent_id": self._agent_id,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat(),
        }
        self.cache.set(self._working_key(memory_id), entry, ttl=WORKING_TTL_SECONDS)
        index = self.cache.get(self._working_index_key()) or []
        index.append(memory_id)
        self.cache.set(self._working_index_key(), index, ttl=WORKING_TTL_SECONDS)
        logger.debug("Stored working memory %s for agent %d", memory_id, self._agent_id)
        return memory_id

    async def _store_persistent(self, memory_id: str, content: str,
                                tier: MemoryTier, importance: float,
                                metadata: Optional[Dict[str, Any]]) -> str:
        """Store in short-term or long-term memory (PostgreSQL + embedding)."""
        embedding = await self.embeddings.embed(content)
        embedding_json = json.dumps(embedding)
        metadata_json = json.dumps(metadata) if metadata else None
        now = datetime.utcnow()
        async with self._db_pool.acquire() as conn:
            await conn.execute(
                """INSERT INTO agent_memory_records
                   (memory_id, agent_id, content, tier, importance,
                    embedding, metadata_json, created_at, last_accessed, access_count)
                   VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $8, 0)""",
                memory_id, self._agent_id, content, tier.value,
                importance, embedding_json, metadata_json, now,
            )
        logger.info("Stored %s memory %s for agent %d (importance=%.2f)",
                     tier.value, memory_id, self._agent_id, importance)
        return memory_id

    async def recall(self, query: str, limit: int = 5,
                     min_importance: float = 0.0,
                     tiers: Optional[List[MemoryTier]] = None) -> List[MemoryEntry]:
        """Cross-tier recall by semantic similarity + importance."""
        if tiers is None:
            tiers = list(MemoryTier)
        results: List[MemoryEntry] = []
        if MemoryTier.WORKING in tiers:
            results.extend(await self._recall_working(query))
        persistent_tiers = [t for t in tiers if t != MemoryTier.WORKING]
        if persistent_tiers:
            results.extend(
                await self._recall_persistent(query, limit * 2, min_importance, persistent_tiers))
        results = [r for r in results if r.importance >= min_importance]
        results.sort(
            key=lambda e: (e.similarity or 0.0) * SIMILARITY_WEIGHT + e.importance * IMPORTANCE_WEIGHT,
            reverse=True)
        return results[:limit]

    async def _recall_working(self, query: str) -> List[MemoryEntry]:
        """Recall from working memory via keyword overlap."""
        index = self.cache.get(self._working_index_key()) or []
        entries: List[MemoryEntry] = []
        query_words = set(query.lower().split())
        for mid in index:
            raw = self.cache.get(self._working_key(mid))
            if raw is None:
                continue
            content_words = set(raw["content"].lower().split())
            overlap = len(query_words & content_words)
            similarity = overlap / max(len(query_words), 1)
            entries.append(MemoryEntry(
                memory_id=raw["memory_id"], content=raw["content"],
                tier=MemoryTier.WORKING, importance=raw["importance"],
                agent_id=raw["agent_id"], metadata=raw.get("metadata"),
                created_at=raw.get("created_at"), similarity=similarity))
        return entries

    async def _recall_persistent(self, query: str, limit: int,
                                 min_importance: float,
                                 tiers: List[MemoryTier]) -> List[MemoryEntry]:
        """Recall from PostgreSQL using vector cosine similarity."""
        query_embedding = await self.embeddings.embed(query)
        tier_values = [t.value for t in tiers]
        async with self._db_pool.acquire() as conn:
            rows = await conn.fetch(
                """SELECT memory_id, content, tier, importance, metadata_json,
                          created_at,
                          1 - (embedding::vector <=> $1::vector) AS similarity
                   FROM agent_memory_records
                   WHERE agent_id = $2 AND tier = ANY($3::text[])
                         AND importance >= $4
                   ORDER BY embedding::vector <=> $1::vector
                   LIMIT $5""",
                json.dumps(query_embedding), self._agent_id,
                tier_values, min_importance, limit)
        memory_ids = [row["memory_id"] for row in rows]
        if memory_ids:
            async with self._db_pool.acquire() as conn:
                await conn.execute(
                    """UPDATE agent_memory_records
                       SET last_accessed = $1, access_count = access_count + 1
                       WHERE memory_id = ANY($2::text[])""",
                    datetime.utcnow(), memory_ids)
        entries: List[MemoryEntry] = []
        for row in rows:
            meta = json.loads(row["metadata_json"]) if row["metadata_json"] else None
            entries.append(MemoryEntry(
                memory_id=row["memory_id"], content=row["content"],
                tier=MemoryTier(row["tier"]), importance=row["importance"],
                agent_id=self._agent_id, metadata=meta,
                created_at=row["created_at"].isoformat() if row["created_at"] else None,
                similarity=float(row["similarity"]) if row["similarity"] is not None else 0.0))
        return entries

    async def consolidate(self) -> Dict[str, int]:
        """Promote important short-term to long-term. Decay old ones."""
        now = datetime.utcnow()
        promoted = decayed = deleted = 0
        async with self._db_pool.acquire() as conn:
            # Promote SHORT_TERM with importance > 0.8 and age > 7 days
            result = await conn.execute(
                """UPDATE agent_memory_records SET tier = $1
                   WHERE agent_id = $2 AND tier = $3
                         AND importance > $4 AND created_at < $5""",
                MemoryTier.LONG_TERM.value, self._agent_id,
                MemoryTier.SHORT_TERM.value, PROMOTION_THRESHOLD,
                now - timedelta(days=PROMOTION_MIN_AGE_DAYS))
            promoted = int(result.split()[-1]) if result else 0
            # Decay SHORT_TERM importance by 5% for memories not accessed in a week
            result = await conn.execute(
                """UPDATE agent_memory_records
                   SET importance = GREATEST(0.0, importance * (1.0 - $1))
                   WHERE agent_id = $2 AND tier = $3 AND last_accessed < $4""",
                DECAY_RATE_PER_WEEK, self._agent_id,
                MemoryTier.SHORT_TERM.value, now - timedelta(weeks=1))
            decayed = int(result.split()[-1]) if result else 0
            # Delete SHORT_TERM with importance < 0.1 and age > 30 days
            result = await conn.execute(
                """DELETE FROM agent_memory_records
                   WHERE agent_id = $1 AND tier = $2
                         AND importance < $3 AND created_at < $4""",
                self._agent_id, MemoryTier.SHORT_TERM.value,
                CLEANUP_MIN_IMPORTANCE, now - timedelta(days=SHORT_TERM_MAX_AGE_DAYS))
            deleted = int(result.split()[-1]) if result else 0
        logger.info("Consolidated agent %d: promoted=%d, decayed=%d, deleted=%d",
                     self._agent_id, promoted, decayed, deleted)
        return {"promoted": promoted, "decayed": decayed, "deleted": deleted}

    async def forget(self, max_age_days: int = 90, min_importance: float = 0.1) -> int:
        """Clean up low-importance old memories (never deletes LONG_TERM)."""
        cutoff = datetime.utcnow() - timedelta(days=max_age_days)
        async with self._db_pool.acquire() as conn:
            result = await conn.execute(
                """DELETE FROM agent_memory_records
                   WHERE agent_id = $1 AND importance < $2
                         AND created_at < $3 AND tier != $4""",
                self._agent_id, min_importance, cutoff, MemoryTier.LONG_TERM.value)
            deleted = int(result.split()[-1]) if result else 0
        logger.info("Forgot %d old memories for agent %d", deleted, self._agent_id)
        return deleted

    async def get_stats(self) -> Dict[str, Any]:
        """Return memory statistics per tier."""
        async with self._db_pool.acquire() as conn:
            rows = await conn.fetch(
                """SELECT tier, COUNT(*) AS count,
                          AVG(importance) AS avg_importance,
                          MIN(created_at) AS oldest, MAX(created_at) AS newest
                   FROM agent_memory_records WHERE agent_id = $1
                   GROUP BY tier""", self._agent_id)
        stats: Dict[str, Any] = {"agent_id": self._agent_id, "tiers": {}, "total": 0}
        for row in rows:
            stats["tiers"][row["tier"]] = {
                "count": row["count"],
                "avg_importance": round(float(row["avg_importance"]), 3) if row["avg_importance"] else 0.0,
                "oldest": row["oldest"].isoformat() if row["oldest"] else None,
                "newest": row["newest"].isoformat() if row["newest"] else None,
            }
            stats["total"] += row["count"]
        # Add working memory count from cache
        index = self.cache.get(self._working_index_key()) or []
        working_count = sum(1 for mid in index if self.cache.get(self._working_key(mid)) is not None)
        stats["tiers"]["working"] = {"count": working_count}
        stats["total"] += working_count
        return stats


async def get_memory_hierarchy(agent_id: int, db_pool: Any) -> MemoryHierarchy:
    """Factory function to create a MemoryHierarchy instance."""
    return MemoryHierarchy(agent_id=agent_id, db_pool=db_pool)
