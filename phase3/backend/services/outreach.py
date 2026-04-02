"""
Outreach — 统一的对外触达模块。

合并：marketing_engine + social_publisher + proactive_agent
所有"向外推送内容/消息"的功能归到这里。
"""
# Re-export for backward compatibility
from services.marketing_engine import MarketingEngine  # noqa: F401
from services.social_publisher import TelegramPublisher, get_publisher  # noqa: F401
from services.proactive_agent import ProactiveAgent  # noqa: F401

__all__ = ["MarketingEngine", "TelegramPublisher", "get_publisher", "ProactiveAgent"]
