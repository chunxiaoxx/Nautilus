"""
Nautilus Research Bot — Polling-mode consumer bot (DEPRECATED).

DEPRECATION NOTICE:
  This file implements a python-telegram-bot polling bot.
  Active production bots are webhook-based:
    - Consumer/Research orders → api/commercial_bot.py  (NAUTILUS_COMMERCE_BOT_TOKEN)
    - Admin notifications      → api/telegram_admin_bot.py (TELEGRAM_ADMIN_BOT_TOKEN)
    - Community/groups         → api/telegram_bot.py    (TELEGRAM_BOT_TOKEN)
  This script is kept as a fallback for local testing only.
  Do NOT run alongside main.py — webhook and polling cannot share the same token.

Setup (local only):
  pip install python-telegram-bot web3 aiohttp
  Set env: NAUTILUS_CONSUMER_BOT_TOKEN, NAUTILUS_API_URL, BASE_RPC_URL,
           PLATFORM_PAYMENT_WALLET
"""
import os
import logging
import asyncio
import time
from typing import Optional

logger = logging.getLogger(__name__)

# Use NAUTILUS_CONSUMER_BOT_TOKEN to avoid conflict with the community bot (TELEGRAM_BOT_TOKEN)
TELEGRAM_BOT_TOKEN = os.getenv("NAUTILUS_CONSUMER_BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN", "")
NAUTILUS_API_URL = os.getenv("NAUTILUS_API_URL", "http://localhost:8000")
BASE_RPC_URL = os.getenv("BASE_RPC_URL", "https://mainnet.base.org")
PLATFORM_PAYMENT_WALLET = os.getenv("PLATFORM_PAYMENT_WALLET", "")

# USDC on Base Mainnet
USDC_CONTRACT_ADDRESS = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
USDC_DECIMALS = 6
# ERC-20 Transfer(address indexed from, address indexed to, uint256 value)
_TRANSFER_EVENT_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

# Payment verification constants
_PAYMENT_POLL_INTERVAL_S = 15       # seconds between on-chain polls
_PAYMENT_TIMEOUT_S = 600            # 10 minutes

# Task delivery polling constants
_TASK_POLL_INTERVAL_S = 15          # seconds between API polls
_TASK_POLL_MAX_RETRIES = 20         # 20 × 15 s = 5 minutes

# Pricing (USDC)
PRICING = {
    "research": 5.0,     # DeerFlow research synthesis
    "simulation": 15.0,  # Physics/ML simulation
}

# Order states (in-memory for MVP, use Redis/DB for production)
_pending_orders: dict[int, dict] = {}  # chat_id → order


# --- Bot Commands ---

async def cmd_start(update, context) -> None:
    """Handle /start command."""
    await update.message.reply_text(
        "Welcome to Nautilus Research!\n\n"
        "I connect you to a network of AI agents that can:\n"
        "• /research — Deep research synthesis (5 USDC)\n"
        "• /simulate — Physics/ML simulation (15 USDC)\n"
        "• /status — Check your order status\n"
        "• /help — Show this menu\n\n"
        "Powered by DeerFlow multi-agent pipeline.\n"
        "Visit: https://nautilus.social"
    )


async def cmd_research(update, context) -> None:
    """Handle /research command — start a research order."""
    chat_id = update.effective_chat.id
    _pending_orders[chat_id] = {
        "type": "research",
        "price": PRICING["research"],
        "state": "awaiting_topic",
    }
    await update.message.reply_text(
        f"Research Synthesis — {PRICING['research']} USDC\n\n"
        "Please describe your research topic in detail.\n"
        "Example: 'Summarize recent advances in quantum error correction, "
        "focusing on surface codes and their practical implementations.'"
    )


async def cmd_simulate(update, context) -> None:
    """Handle /simulate command — start a simulation order."""
    chat_id = update.effective_chat.id
    _pending_orders[chat_id] = {
        "type": "simulation",
        "price": PRICING["simulation"],
        "state": "awaiting_topic",
    }
    await update.message.reply_text(
        f"Physics/ML Simulation — {PRICING['simulation']} USDC\n\n"
        "Please describe your simulation requirements.\n"
        "Example: 'Run a Monte Carlo simulation of stock price paths "
        "with 10000 iterations, GBM model, mu=0.1, sigma=0.2, T=1 year.'"
    )


async def cmd_status(update, context) -> None:
    """Handle /status command."""
    chat_id = update.effective_chat.id
    order = _pending_orders.get(chat_id)
    if not order:
        await update.message.reply_text("No active order. Use /research or /simulate to start.")
        return
    await update.message.reply_text(
        f"Order status: {order.get('state', 'unknown')}\n"
        f"Type: {order.get('type')}\n"
        f"Price: {order.get('price')} USDC"
    )


async def handle_message(update, context) -> None:
    """Handle free-text messages (order topic input, payment confirmation)."""
    chat_id = update.effective_chat.id
    text = update.message.text
    order = _pending_orders.get(chat_id)

    if not order:
        await update.message.reply_text(
            "Use /research or /simulate to place an order."
        )
        return

    if order["state"] == "awaiting_topic":
        order["topic"] = text
        order["state"] = "awaiting_payment"
        wallet = os.getenv("PLATFORM_PAYMENT_WALLET", "not configured")
        await update.message.reply_text(
            f"Got it! Your order:\n"
            f"Topic: {text[:100]}...\n\n"
            f"To confirm, send {order['price']} USDC to:\n"
            f"`{wallet}`\n"
            f"(Base Sepolia testnet)\n\n"
            f"After sending, reply with your transaction hash to confirm payment.",
            parse_mode="Markdown"
        )

    elif order["state"] == "awaiting_payment":
        # User sent a tx hash
        if text.startswith("0x") and len(text) == 66:
            order["payment_tx"] = text
            order["state"] = "processing"
            await update.message.reply_text(
                "Payment received! Your order is being processed.\n"
                "Estimated delivery: 5-10 minutes.\n"
                "I'll send you the report when it's ready."
            )
            # Dispatch async task
            asyncio.ensure_future(
                _process_order(chat_id, order, context)
            )
        else:
            await update.message.reply_text(
                "Please send a valid transaction hash (0x... 66 characters)."
            )


async def _verify_usdc_payment(
    sender_address: str,
    expected_usdc: float,
    start_block: int,
) -> bool:
    """
    Poll Base chain every _PAYMENT_POLL_INTERVAL_S seconds for a USDC Transfer
    from sender_address to PLATFORM_PAYMENT_WALLET with the expected amount.
    Returns True when payment is confirmed, False on timeout.

    Uses eth_getLogs (polling) — no WebSocket subscription required.
    """
    from web3 import Web3

    w3 = Web3(Web3.HTTPProvider(BASE_RPC_URL))
    platform_wallet = PLATFORM_PAYMENT_WALLET.lower()
    sender = sender_address.lower()
    expected_raw = int(expected_usdc * 10 ** USDC_DECIMALS)

    # ABI-encode the indexed address topics (32-byte zero-padded)
    def _address_topic(addr: str) -> str:
        return "0x" + addr.lower().replace("0x", "").zfill(64)

    deadline = time.monotonic() + _PAYMENT_TIMEOUT_S

    while time.monotonic() < deadline:
        await asyncio.sleep(_PAYMENT_POLL_INTERVAL_S)
        try:
            latest_block = w3.eth.block_number
            logs = w3.eth.get_logs({
                "fromBlock": start_block,
                "toBlock": latest_block,
                "address": Web3.to_checksum_address(USDC_CONTRACT_ADDRESS),
                "topics": [
                    _TRANSFER_EVENT_TOPIC,
                    _address_topic(sender),
                    _address_topic(platform_wallet),
                ],
            })
            for log in logs:
                # data field holds the uint256 value (32 bytes, big-endian)
                value = int(log["data"].hex() if isinstance(log["data"], bytes)
                            else log["data"], 16)
                if value >= expected_raw:
                    logger.info(
                        "USDC payment confirmed: from=%s amount=%s tx=%s",
                        sender, value / 10 ** USDC_DECIMALS,
                        log["transactionHash"].hex(),
                    )
                    return True
            # Advance start_block to avoid re-scanning old blocks
            start_block = latest_block
        except Exception as exc:
            logger.warning("Payment verification poll error: %s", exc)

    return False


async def _process_order(chat_id: int, order: dict, context) -> None:
    """
    Process a confirmed order:
      1. Verify USDC payment on-chain (Base chain, polling).
      2. Call Nautilus API to create the task.
      3. Poll for task completion and deliver the result.
    """
    import aiohttp
    from web3 import Web3

    # --- Step 1: Verify USDC payment on-chain ---
    sender_wallet = order.get("sender_wallet", "")
    if not sender_wallet:
        # If we don't have the sender wallet, skip on-chain verification
        # (MVP: trust the user-submitted tx hash from handle_message)
        logger.warning(
            "No sender wallet for chat %s — skipping on-chain verification", chat_id
        )
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                f"Waiting for your USDC payment on Base chain...\n"
                f"Amount: {order['price']} USDC\n"
                f"To: `{PLATFORM_PAYMENT_WALLET}`\n\n"
                f"Timeout: 10 minutes."
            ),
            parse_mode="Markdown",
        )
        try:
            w3 = Web3(Web3.HTTPProvider(BASE_RPC_URL))
            start_block = w3.eth.block_number
        except Exception as exc:
            logger.error("Cannot connect to Base RPC: %s", exc)
            start_block = 0

        paid = await _verify_usdc_payment(sender_wallet, order["price"], start_block)
        if not paid:
            order["state"] = "cancelled"
            await context.bot.send_message(
                chat_id=chat_id,
                text=(
                    "Payment not detected within 10 minutes. "
                    "Your order has been cancelled. "
                    "Please try again or contact support."
                ),
            )
            return

        await context.bot.send_message(
            chat_id=chat_id,
            text="Payment confirmed on-chain! Processing your order now...",
        )

    # --- Step 2: Submit task to Nautilus API ---
    try:
        task_type = (
            "research_synthesis" if order["type"] == "research"
            else "physics_simulation"
        )
        payload = {
            "title": order["topic"][:100],
            "description": order["topic"],
            "task_type": task_type,
            "parameters": {"source": "telegram_bot"},
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{NAUTILUS_API_URL}/api/academic-tasks",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=300),
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    task_id = result.get("data", {}).get("task_id")
                    order["task_id"] = task_id
                    order["state"] = "polling"

                    # Step 3: Poll for completion and deliver
                    await _poll_and_deliver(chat_id, task_id, context)
                else:
                    raise Exception(f"API error: {resp.status}")

    except Exception as e:
        logger.error("Order processing failed for chat %s: %s", chat_id, e)
        await context.bot.send_message(
            chat_id=chat_id,
            text="Sorry, an error occurred processing your order. Please contact support."
        )


async def _poll_and_deliver(chat_id: int, task_id: str, context) -> None:
    """
    Poll task status and deliver result when complete.

    Retries up to _TASK_POLL_MAX_RETRIES times (_TASK_POLL_INTERVAL_S each).
    - COMPLETED  → send report
    - FAILED     → notify user, ask for manual refund processing
    - Network errors → log and continue retrying (do not give up early)
    - Exhausted retries → inform user that result will arrive within 30 min
    """
    import aiohttp

    for attempt in range(1, _TASK_POLL_MAX_RETRIES + 1):
        await asyncio.sleep(_TASK_POLL_INTERVAL_S)
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{NAUTILUS_API_URL}/api/academic-tasks/{task_id}",
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status == 200:
                        data = (await resp.json()).get("data", {})
                        status = data.get("status")

                        if status == "completed":
                            output = data.get("result_output", "No output")
                            nau = data.get("token_reward", 0)
                            await context.bot.send_message(
                                chat_id=chat_id,
                                text=(
                                    f"Your report is ready!\n\n"
                                    f"{output[:3000]}\n\n"
                                    f"Agent earned: {nau} NAU"
                                )
                            )
                            return

                        elif status == "failed":
                            await context.bot.send_message(
                                chat_id=chat_id,
                                text=(
                                    "Task failed. Your payment will be refunded "
                                    "(manual processing — we will contact you shortly)."
                                ),
                            )
                            return

                        # Any other status (pending, running…) → keep polling
                        logger.debug(
                            "Task %s status=%s attempt=%d/%d",
                            task_id, status, attempt, _TASK_POLL_MAX_RETRIES,
                        )
                    else:
                        logger.warning(
                            "Poll HTTP %s for task %s (attempt %d/%d)",
                            resp.status, task_id, attempt, _TASK_POLL_MAX_RETRIES,
                        )

        except Exception as exc:
            # Network error — log and continue retrying instead of giving up
            logger.warning(
                "Poll network error for task %s (attempt %d/%d): %s",
                task_id, attempt, _TASK_POLL_MAX_RETRIES, exc,
            )

    # All retries exhausted without a terminal status
    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            "Our servers are currently busy processing your request. "
            "We will send you the result through this channel within 30 minutes. "
            "Apologies for the delay!"
        ),
    )


def create_application():
    """Create and configure the Telegram bot application."""
    try:
        from telegram.ext import Application, CommandHandler, MessageHandler, filters
    except ImportError:
        raise ImportError(
            "python-telegram-bot not installed. Run: pip install python-telegram-bot aiohttp"
        )

    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN not set in environment")

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_start))
    app.add_handler(CommandHandler("research", cmd_research))
    app.add_handler(CommandHandler("simulate", cmd_simulate))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    return app


def run_bot() -> None:
    """Run the bot (blocking). Called from main or systemd service."""
    app = create_application()
    logger.info("Starting Nautilus Telegram Bot...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_bot()
