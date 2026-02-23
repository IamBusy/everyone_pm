from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from eopm.core.stage_manager import WorkflowState


def load_messages(path: Path) -> list[dict]:
    """Load messages from a session file.

    Legacy format: list of message dicts
    New format: dict with 'messages' and 'workflow_state' keys
    """
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    # Legacy format: just a list of messages
    if isinstance(data, list):
        return data

    # New format: dict with messages and workflow_state
    if isinstance(data, dict):
        return data.get("messages", [])

    raise ValueError(f"Invalid session file format at {path}")


def load_workflow_state(path: Path) -> WorkflowState | None:
    """Load workflow state from a session file."""
    if not path.exists():
        return None

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    # Legacy format: no workflow state
    if isinstance(data, list):
        return None

    # New format: dict with workflow_state
    if isinstance(data, dict):
        state_data = data.get("workflow_state")
        if state_data:
            return WorkflowState.from_dict(state_data)

    return None


def save_session(
    path: Path, messages: list[dict], workflow_state: WorkflowState | None = None
) -> None:
    """Save both messages and workflow state to the session file."""
    path.parent.mkdir(parents=True, exist_ok=True)

    data: dict[str, Any] = {"messages": messages}

    if workflow_state:
        data["workflow_state"] = workflow_state.to_dict()

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def save_messages(path: Path, messages: list[dict]) -> None:
    """Legacy function for backward compatibility.

    Deprecated: Use save_session() instead.
    """
    # Try to preserve existing workflow state
    existing_state = load_workflow_state(path)
    save_session(path, messages, existing_state)
