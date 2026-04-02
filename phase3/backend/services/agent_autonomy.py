"""Agent Autonomy Engine — 自主意识驱动的投标和市场扫描

生存等级与投标策略映射：
- ELITE（最高）：min_nau_threshold=5, selectivity=0.3（只接30%的机会）
- MATURE：min_nau_threshold=3, selectivity=0.5
- GROWING：min_nau_threshold=1, selectivity=0.7
- STRUGGLING：min_nau_threshold=0.5, selectivity=0.9
- CRITICAL/WARNING：min_nau_threshold=0, selectivity=1.0（接一切）
"""
import json
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# 生存等级 → 投标策略映射
_STRATEGY_MAP = {
    "ELITE":     {"min_nau_threshold": 5.0,  "selectivity": 0.3, "bid_multiplier": 1.5, "max_concurrent_bids": 3},
    "MATURE":    {"min_nau_threshold": 3.0,  "selectivity": 0.5, "bid_multiplier": 1.2, "max_concurrent_bids": 5},
    "GROWING":   {"min_nau_threshold": 1.0,  "selectivity": 0.7, "bid_multiplier": 1.0, "max_concurrent_bids": 8},
    "STRUGGLING": {"min_nau_threshold": 0.5, "selectivity": 0.9, "bid_multiplier": 0.9, "max_concurrent_bids": 10},
    "WARNING":   {"min_nau_threshold": 0.0,  "selectivity": 1.0, "bid_multiplier": 0.8, "max_concurrent_bids": 15},
    "CRITICAL":  {"min_nau_threshold": 0.0,  "selectivity": 1.0, "bid_multiplier": 0.8, "max_concurrent_bids": 15},
}
_DEFAULT_STRATEGY = _STRATEGY_MAP["GROWING"]


@dataclass
class BidStrategy:
    min_nau_threshold: float   # 最低接受的 NAU
    selectivity: float         # 0-1，越低越挑剔
    bid_multiplier: float      # 报价 = task.min_bid_nau * multiplier（ELITE 可以报更高）
    max_concurrent_bids: int   # 同时最多投标数


def get_bid_strategy(survival_status: str) -> BidStrategy:
    """根据生存等级返回对应投标策略。未知等级回落到 GROWING 策略。"""
    params = _STRATEGY_MAP.get(survival_status.upper() if survival_status else "", _DEFAULT_STRATEGY)
    return BidStrategy(**params)


def _parse_specialties(specialties_raw: Optional[str]) -> list[str]:
    """解析 specialties 字段（JSON 数组或逗号分隔字符串）。"""
    if not specialties_raw:
        return []
    try:
        parsed = json.loads(specialties_raw)
        if isinstance(parsed, list):
            return [str(s).lower().strip() for s in parsed if s]
    except (json.JSONDecodeError, TypeError):
        pass
    # 降级：逗号分隔
    return [s.lower().strip() for s in specialties_raw.split(",") if s.strip()]


def _task_matches_specialties(task_type: str, specialties: list[str]) -> bool:
    """判断任务类型是否匹配 agent 的专长列表。空专长列表接受所有任务。"""
    if not specialties:
        return True
    return task_type.lower() in specialties


def scan_and_bid(db: Session, agent_id: int) -> list[dict]:
    """
    单个 agent 执行市场扫描并自动投标（同步版本）。

    步骤：
    1. 获取 agent 信息（specialties, survival_status）
    2. 调用 get_bid_strategy(survival_status)
    3. 查询 marketplace_open=True 且 status='pending' 的任务
    4. 过滤匹配专长的任务
    5. 对匹配且高于 min_nau_threshold 的任务自动提交投标
    6. 更新 agent.last_market_scan = now()
    7. 返回提交的投标列表
    """
    from models.database import Agent, AcademicTask, TaskBid
    from models.agent_survival import AgentSurvival
    from sqlalchemy import select

    # 1. 获取 agent
    agent = db.execute(select(Agent).where(Agent.agent_id == agent_id)).scalar_one_or_none()
    if agent is None:
        logger.warning("scan_and_bid: agent_id=%s not found", agent_id)
        return []

    # 获取生存等级
    survival = db.execute(
        select(AgentSurvival).where(AgentSurvival.agent_id == agent_id)
    ).scalar_one_or_none()
    survival_level = survival.survival_level if survival else "GROWING"

    # 2. 投标策略
    strategy = get_bid_strategy(survival_level)
    specialties = _parse_specialties(agent.specialties)

    # 3. 查询开放市场任务
    open_tasks = db.execute(
        select(AcademicTask).where(
            AcademicTask.marketplace_open == True,
            AcademicTask.status == "pending",
        )
    ).scalars().all()

    # 4 & 5. 过滤 + 投标
    submitted: list[dict] = []

    # 检查当前待处理投标数（不超过 max_concurrent_bids）
    existing_pending = len(
        db.execute(
            select(TaskBid).where(
                TaskBid.agent_id == agent_id,
                TaskBid.status == "pending",
            )
        ).scalars().all()
    )

    for task in open_tasks:
        if len(submitted) + existing_pending >= strategy.max_concurrent_bids:
            break

        # 专长匹配
        if not _task_matches_specialties(task.task_type, specialties):
            continue

        # NAU 阈值过滤
        task_min_bid = task.min_bid_nau or 0.0
        if task_min_bid < strategy.min_nau_threshold:
            continue

        # 选择性过滤（selectivity < 1.0 时按概率跳过低价任务）
        if strategy.selectivity < 1.0:
            normalized_value = task_min_bid / max(strategy.min_nau_threshold, 1.0)
            accept_threshold = 1.0 / max(strategy.selectivity, 0.01)
            if normalized_value < accept_threshold:
                continue

        # 检查是否已经对该任务投标（用 first() 避免重复记录导致 MultipleResultsFound）
        existing_bid = db.execute(
            select(TaskBid).where(
                TaskBid.agent_id == agent_id,
                TaskBid.task_id == task.task_id,
            )
        ).scalars().first()
        if existing_bid is not None:
            continue

        # 计算报价
        bid_nau = round(task_min_bid * strategy.bid_multiplier, 4)

        # 创建投标记录
        bid = TaskBid(
            id=str(uuid.uuid4()),
            task_id=task.task_id,
            agent_id=agent_id,
            bid_nau=bid_nau,
            estimated_minutes=10,
            message=f"Auto-bid from agent {agent_id} (level: {survival_level})",
            status="pending",
            created_at=datetime.utcnow(),
        )
        db.add(bid)
        submitted.append({
            "bid_id": bid.id,
            "task_id": task.task_id,
            "agent_id": agent_id,
            "bid_nau": bid_nau,
            "survival_level": survival_level,
        })

    # 6. 更新 last_market_scan
    agent.last_market_scan = datetime.utcnow()

    db.commit()
    logger.info(
        "scan_and_bid: agent_id=%s level=%s scanned=%d submitted=%d",
        agent_id, survival_level, len(open_tasks), len(submitted),
    )
    return submitted


def run_autonomy_cycle(db_factory) -> dict:
    """
    遍历所有 autonomy_enabled=True 的 agent，调用 scan_and_bid()。
    同步版本，兼容 SessionLocal (cron_registry 使用)。

    返回:
        {"scanned": N, "bids_submitted": M, "errors": [...]}
    """
    from models.database import Agent
    from sqlalchemy import select

    scanned = 0
    bids_submitted = 0
    errors: list[str] = []

    db = db_factory()
    try:
        agents = db.execute(
            select(Agent).where(Agent.autonomy_enabled == True)
        ).scalars().all()
        agent_ids = [a.agent_id for a in agents]
    finally:
        db.close()

    for agent_id in agent_ids:
        scanned += 1
        db = db_factory()
        try:
            bids = scan_and_bid(db, agent_id)
            bids_submitted += len(bids)
        except Exception as exc:
            msg = f"agent_id={agent_id}: {exc}"
            logger.exception("run_autonomy_cycle error: %s", msg)
            errors.append(msg)
            try:
                db.rollback()
            except Exception:
                pass
        finally:
            db.close()

    logger.info(
        "run_autonomy_cycle complete: scanned=%d bids_submitted=%d errors=%d",
        scanned, bids_submitted, len(errors),
    )
    return {"scanned": scanned, "bids_submitted": bids_submitted, "errors": errors}
