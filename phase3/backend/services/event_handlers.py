"""
Event Handlers — 集中注册所有平台事件处理器
仿 Claude Code KAIROS：事件触发 > 定时轮询

当前注册的处理器：
- platform.snapshot  → 检测异常，创建元任务
- task.completed     → 更新 capability_stat，触发 reputation 更新
- task.rated         → 更新 reputation EWMA
- agent.registered   → 初始化 agent_memory（日志记录）
"""
import logging
import asyncio
from services.event_bus import on, Events

logger = logging.getLogger(__name__)


@on(Events.PLATFORM_SNAPSHOT)
async def handle_platform_snapshot(payload: dict):
    """
    Observatory 每次快照后触发。
    若有异常，调用 meta_task_generator.process_anomalies()。
    使用懒加载避免循环依赖。
    """
    anomalies = payload.get("anomalies", [])
    if not anomalies:
        return
    try:
        from services.meta_task_generator import process_anomalies
        from utils.database import SessionLocal
        asyncio.create_task(_run_meta_task_generation(anomalies, SessionLocal))
    except Exception as e:
        logger.warning(f"Meta task generation trigger failed: {e}")


async def _run_meta_task_generation(anomalies, db_factory):
    try:
        from services.meta_task_generator import process_anomalies
        new_task_ids = await process_anomalies(anomalies, db_factory)
        if new_task_ids:
            logger.info(f"Created {len(new_task_ids)} meta tasks from anomalies: {new_task_ids}")
    except Exception as e:
        logger.error(f"Meta task generation failed: {e}")


@on(Events.TASK_COMPLETED)
async def handle_task_completed(payload: dict):
    """任务完成 → 更新 capability_stat（非阻塞）"""
    task_id = payload.get("task_id")
    agent_id = payload.get("agent_id")
    task_type = payload.get("task_type")
    success = payload.get("success", True)
    quality = payload.get("quality_rating")
    if not all([task_id, agent_id, task_type]):
        return
    try:
        from utils.database import SessionLocal
        asyncio.create_task(_run_capability_update(agent_id, task_type, success, quality, SessionLocal))
    except Exception as e:
        logger.warning(f"Capability update trigger failed: {e}")


async def _run_capability_update(agent_id, task_type, success, quality, db_factory):
    try:
        from services.capability_evolution import record_task_outcome
        db = db_factory()
        try:
            await record_task_outcome(db, agent_id, task_type, success, quality)
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Capability update failed: {e}")


@on(Events.TASK_RATED)
async def handle_task_rated(payload: dict):
    """任务评分 → 更新 reputation EWMA（非阻塞）"""
    agent_id = payload.get("agent_id")
    rating = payload.get("rating")
    if not agent_id or not rating:
        return
    try:
        from utils.database import SessionLocal
        asyncio.create_task(_run_reputation_update(agent_id, rating, SessionLocal))
    except Exception as e:
        logger.warning(f"Reputation update trigger failed: {e}")


async def _run_reputation_update(agent_id, rating, db_factory):
    try:
        from services.reputation import update_reputation
        db = db_factory()
        try:
            update_reputation(db, agent_id, rating)
            db.commit()
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Reputation update failed: {e}")


@on(Events.AGENT_REGISTERED)
async def handle_agent_registered(payload: dict):
    agent_id = payload.get("agent_id")
    name = payload.get("name", "unknown")
    logger.info(f"New agent registered: {name} (id={agent_id}) — initializing in platform memory")


def register_all_handlers():
    """
    调用此函数触发模块导入，完成 @on() 装饰器注册。
    在 main.py startup 中调用一次即可。
    """
    logger.info("Event handlers registered: platform.snapshot, task.completed, task.rated, agent.registered")
