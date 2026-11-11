"""Supabase data access for the current single-chat UI.

Every client passed here must be authenticated as the current user.
Database Row Level Security is the final ownership check.
"""

from typing import Any

from supabase import Client


def _insert_id(client: Client, table: str, payload: dict[str, Any]) -> str:
    response = (
        client.table(table)
        .insert(payload)
        .select("id")
        .execute()
    )
    if not response.data:
        raise RuntimeError(f"Could not insert a row into {table}.")
    return str(response.data[0]["id"])


def create_conversation(client: Client, user_id: str, title: str) -> str:
    return _insert_id(client, "conversations", {
        "user_id": user_id,
        "title": title or "New conversation",
    })


def save_message(
    client: Client, conversation_id: str, role: str, content: str
) -> str:
    if role not in {"user", "assistant"}:
        raise ValueError("Only user and assistant messages are stored.")
    return _insert_id(client, "messages", {
        "conversation_id": conversation_id,
        "role": role,
        "content": content,
    })


def save_situation(
    client: Client, conversation_id: str, situation: dict[str, Any]
) -> str:
    """Start a NEW evaluation run; prior runs are never updated."""
    return _insert_id(client, "evaluation_runs", {
        "conversation_id": conversation_id,
        "situation": situation,
        "status": "situation_saved",
    })


def save_evaluation(
    client: Client, run_id: str, evaluation: dict[str, Any]
) -> None:
    """Complete the specific run associated with this situation."""
    result = (
        client.table("evaluation_runs")
        .update({
            "evaluation": evaluation,
            "status": "completed",
        })
        .eq("id", run_id)
        .select("id")
        .execute()
    )
    if not result.data:
        raise RuntimeError("Could not update the evaluation run.")


def mark_evaluation_failed(client: Client, run_id: str, reason: str) -> None:
    result = (
        client.table("evaluation_runs")
        .update({
            "status": "failed",
            "error": reason[:500],
        })
        .eq("id", run_id)
        .select("id")
        .execute()
    )
    if not result.data:
        raise RuntimeError("Could not mark the evaluation as failed.")
