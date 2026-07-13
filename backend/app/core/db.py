import logging
import os
from typing import Any, Dict, List

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import Json

logger = logging.getLogger("uvicorn.error")
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()


def get_connection():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not configured.")
    return psycopg2.connect(DATABASE_URL)


def ensure_schema() -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS crisis_events (
                    id BIGSERIAL PRIMARY KEY,
                    report_id TEXT UNIQUE NOT NULL,
                    raw_text TEXT,
                    source TEXT,
                    timestamp TIMESTAMPTZ DEFAULT NOW(),
                    translated_english TEXT,
                    location_extracted TEXT,
                    situation_type TEXT,
                    severity TEXT,
                    confidence NUMERIC(4, 2),
                    impact_details JSONB,
                    status TEXT DEFAULT 'Pending',
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS agent_logs (
                    id BIGSERIAL PRIMARY KEY,
                    report_id TEXT NOT NULL,
                    agent_name TEXT NOT NULL,
                    action_taken TEXT,
                    payload JSONB,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS simulated_states (
                    id BIGSERIAL PRIMARY KEY,
                    report_id TEXT NOT NULL,
                    recommended_actions JSONB,
                    simulated_outcome JSONB,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
                """
            )
        conn.commit()


def initialize_database() -> None:
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not configured.")

    ensure_schema()
    logger.info("[Database] PostgreSQL schema initialized successfully.")


def sync_crisis_event(report_id: str, **payload: Any) -> Dict[str, Any]:
    if not payload:
        return {"status": "noop"}

    columns = ["report_id", *payload.keys()]
    values = [report_id]
    for key, value in payload.items():
        if isinstance(value, (dict, list)):
            values.append(Json(value))
        else:
            values.append(value)

    update_assignments = [f"{key} = EXCLUDED.{key}" for key in payload.keys() if key != "report_id"]
    query = f"""
        INSERT INTO crisis_events ({', '.join(columns)})
        VALUES ({', '.join(['%s'] * len(columns))})
        ON CONFLICT (report_id) DO UPDATE SET
        {', '.join(update_assignments + ['updated_at = NOW()'])}
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, values)
            conn.commit()
    return {"status": "ok"}


def log_agent_action(report_id: str, agent_name: str, action_taken: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO agent_logs (report_id, agent_name, action_taken, payload)
                VALUES (%s, %s, %s, %s)
                """,
                (report_id, agent_name, action_taken, Json(payload)),
            )
            conn.commit()
    return {"status": "ok"}


def save_simulated_state(report_id: str, recommended_actions: list, simulated_outcome: Dict[str, Any]) -> Dict[str, Any]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO simulated_states (report_id, recommended_actions, simulated_outcome)
                VALUES (%s, %s, %s)
                """,
                (report_id, Json(recommended_actions), Json(simulated_outcome)),
            )
            conn.commit()
    return {"status": "ok"}


def fetch_latest_reports(limit: int = 10) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT report_id, raw_text, source, translated_english, location_extracted,
                       situation_type, severity, confidence, impact_details, status,
                       created_at, updated_at
                FROM crisis_events
                ORDER BY updated_at DESC, created_at DESC
                LIMIT %s
                """,
                (limit,),
            )
            rows = cur.fetchall()

    return [
        {
            "report_id": row[0],
            "raw_text": row[1],
            "source": row[2],
            "translated_english": row[3],
            "location_extracted": row[4],
            "situation_type": row[5],
            "severity": row[6],
            "confidence": float(row[7]) if row[7] is not None else None,
            "impact_details": row[8],
            "status": row[9],
            "created_at": row[10].isoformat() if row[10] else None,
            "updated_at": row[11].isoformat() if row[11] else None,
        }
        for row in rows
    ]


initialize_database()
