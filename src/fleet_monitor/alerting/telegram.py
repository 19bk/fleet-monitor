"""Telegram delivery for alert batches."""

from __future__ import annotations

import os
from typing import Any

import requests

from fleet_monitor.storage.store import AlertRecord


class TelegramAlerter:
    def __init__(self, bot_token: str | None = None, chat_id: str | None = None) -> None:
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")

    @property
    def enabled(self) -> bool:
        return bool(self.bot_token and self.chat_id)

    def send_alerts(self, alerts: list[AlertRecord]) -> dict[str, Any]:
        if not alerts:
            return {"sent": 0, "enabled": self.enabled}
        if not self.enabled:
            return {"sent": 0, "enabled": False, "reason": "Telegram credentials not configured"}

        sent = 0
        for alert in alerts:
            payload = {
                "chat_id": self.chat_id,
                "text": (
                    f"[{alert.severity.upper()}] {alert.title}\n"
                    f"Device: {alert.device_id}\n"
                    f"Health: {alert.health_score:.0%}\n"
                    f"Risk: {alert.failure_probability:.0%}\n"
                    f"Mode: {alert.predicted_failure_mode}\n"
                    f"{alert.message}"
                ),
            }
            response = requests.post(
                f"https://api.telegram.org/bot{self.bot_token}/sendMessage",
                json=payload,
                timeout=10,
            )
            response.raise_for_status()
            sent += 1
        return {"sent": sent, "enabled": True}

