"""Thin wrapper — all logic moved to services.platform_brain."""
from services.platform_brain import (  # noqa: F401
    DailyGoals, DailyPlan, DailyPlanGenerator, GoalEngine,
    PerformanceSnapshot, PerformanceTracker, ProactiveAction,
    ProactiveActionEngine, RehoboamExecutive, YesterdayReview,
    get_executive,
)
