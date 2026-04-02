"""
Proposal Consensus
声誉加权投票系统，仿 DGM-H compute-aware planning：
- TRUSTED tier (reputation>=80): 投票权重 3.0
- ESTABLISHED (>=60): 2.0
- NEWCOMER (>=30): 1.0
- PROBATION (<30): 0.5
"""
import logging

logger = logging.getLogger(__name__)

# Consensus thresholds by change type
_THRESHOLDS = {
    "task_template":     {"score": 6,  "count": 3},
    "routing_weights":   {"score": 10, "count": 5},
    "reward_parameters": {"score": 15, "count": 7},
    "default":           {"score": 6,  "count": 3},
}


def get_vote_weight(reputation_score: float) -> float:
    """根据声誉分返回投票权重"""
    if reputation_score >= 80:
        return 3.0
    if reputation_score >= 60:
        return 2.0
    if reputation_score >= 30:
        return 1.0
    return 0.5


def check_consensus_reached(
    vote_score: float,
    vote_count: int,
    change_type: str = "default",
) -> tuple[bool, str]:
    """
    判断是否达到共识。
    返回 (reached: bool, reason: str)
    不同类型的改变需要不同阈值（仿 DGM-H 保守策略）：
    - task_template: score>=6 且 count>=3
    - routing_weights: score>=10 且 count>=5
    - reward_parameters: score>=15 且 count>=7
    - default: score>=6 且 count>=3
    """
    t = _THRESHOLDS.get(change_type, _THRESHOLDS["default"])
    min_score, min_count = t["score"], t["count"]

    if vote_score >= min_score and vote_count >= min_count:
        return True, (
            f"Consensus reached: score={vote_score:.1f}>={min_score}, "
            f"count={vote_count}>={min_count} for change_type='{change_type}'"
        )
    return False, (
        f"Not yet: need score>={min_score} (have {vote_score:.1f}), "
        f"count>={min_count} (have {vote_count}) for change_type='{change_type}'"
    )


def get_proposal_status(
    vote_score: float,
    vote_count: int,
    change_type: str = "default",
) -> str:
    """返回 'pending'/'voting'/'accepted'/'rejected'"""
    if vote_count == 0:
        return "pending"

    # Check for rejection: heavily negative with enough votes
    if vote_score < -5 and vote_count >= 3:
        return "rejected"

    # Check for acceptance
    reached, _ = check_consensus_reached(vote_score, vote_count, change_type)
    if reached:
        return "accepted"

    return "voting"


def on_consensus_reached(proposal_id: str, proposed_change: dict, db_factory) -> None:
    """
    当提案达到 accepted 共识时调用。
    自动创建 A/B 沙箱实验。
    db_factory: 同步 SessionLocal（不是 async）。
    """
    try:
        from services.sandbox import create_experiment
        db = db_factory()
        try:
            exp_id = create_experiment(db, proposal_id, proposed_change)
            if exp_id:
                logger.info("consensus: created sandbox experiment %s for proposal %s", exp_id, proposal_id)
            else:
                logger.warning("consensus: failed to create experiment for proposal %s", proposal_id)
        finally:
            db.close()
    except Exception as e:
        logger.error("consensus: on_consensus_reached failed: %s", e)
