"""
logger.py — Structured event logger.

Logs all key workflow events to both stdout (human-readable)
and a JSON log file (closira_session.log) for auditability.
"""

import json
import os
from datetime import datetime, timezone
from rich.console import Console

console = Console()
LOG_FILE = "closira_session.log"


def _write(entry: dict):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def log_event(event_type: str, detail: str, extra: dict = None):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event_type,
        "detail": detail,
    }
    if extra:
        entry.update(extra)
    _write(entry)


def log_escalation(reason: str, trigger: str, conversation_snapshot: list):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": "ESCALATION_TRIGGERED",
        "reason": reason,
        "trigger": trigger,
        "conversation_length": len(conversation_snapshot),
    }
    _write(entry)
    console.print(f"\n[bold red]⚠  ESCALATION[/bold red] → {reason}")


def log_stage_transition(from_stage: str, to_stage: str):
    log_event("STAGE_TRANSITION", f"{from_stage} → {to_stage}")


def log_session_start(session_id: str):
    # Clear previous log for this session
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
    log_event("SESSION_START", "New session started", {"session_id": session_id})
    console.print(f"[dim]Session ID: {session_id}[/dim]")


def log_session_end(session_id: str):
    log_event("SESSION_END", "Session completed", {"session_id": session_id})
