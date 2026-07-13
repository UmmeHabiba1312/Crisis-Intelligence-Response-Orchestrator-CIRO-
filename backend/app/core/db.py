import logging
import os
from typing import Any, Dict

from dotenv import load_dotenv
from supabase import Client, create_client

logger = logging.getLogger("uvicorn.error")
load_dotenv()

url: str = os.environ.get("SUPABASE_URL", "")
key: str = os.environ.get("SUPABASE_KEY", "")


class MockSupabaseTable:
    def __init__(self, name: str):
        self.name = name

    def insert(self, data: Dict[str, Any]):
        logger.info(f"[Mock DB - {self.name}] INSERT: {data}")
        return self

    def upsert(self, data: Dict[str, Any]):
        logger.info(f"[Mock DB - {self.name}] UPSERT: {data}")
        return self

    def execute(self):
        return {"data": [], "count": 0}


class MockSupabaseClient:
    def table(self, name: str):
        return MockSupabaseTable(name)


if url and key:
    try:
        supabase: Client = create_client(url, key)
        logger.info("[Supabase] Successfully initialized real client.")
    except Exception as exc:
        logger.warning(
            f"[Supabase Warning] Failed to initialize real client: {exc}. Using mock client fallback."
        )
        supabase = MockSupabaseClient()
else:
    logger.warning("[Supabase Warning] SUPABASE_URL or SUPABASE_KEY not set. Using mock client fallback.")
    supabase = MockSupabaseClient()


def sync_crisis_event(report_id: str, **payload: Any):
    data = {"report_id": report_id, **payload}
    return supabase.table("crisis_events").upsert(data).execute()


def log_agent_action(report_id: str, agent_name: str, action_taken: str, payload: Dict[str, Any]):
    return supabase.table("agent_logs").insert(
        {
            "report_id": report_id,
            "agent_name": agent_name,
            "action_taken": action_taken,
            "payload": payload,
        }
    ).execute()


def save_simulated_state(report_id: str, recommended_actions: list, simulated_outcome: Dict[str, Any]):
    return supabase.table("simulated_states").insert(
        {
            "report_id": report_id,
            "recommended_actions": recommended_actions,
            "simulated_outcome": simulated_outcome,
        }
    ).execute()
