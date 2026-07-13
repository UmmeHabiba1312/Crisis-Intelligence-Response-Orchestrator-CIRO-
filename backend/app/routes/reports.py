import logging
from typing import Any, Dict

from fastapi import APIRouter, BackgroundTasks

from app.agents.analysis import run_analysis_agent
from app.agents.ingestion import run_ingestion_agent
from app.agents.orchestrator import run_orchestrator_agent
from app.agents.simulation import run_simulation_agent
from app.core.db import log_agent_action, save_simulated_state, supabase, sync_crisis_event
from app.core.schemas import RawReport

router = APIRouter()
logger = logging.getLogger("uvicorn.error")


def serialize_model(model: Any) -> Dict[str, Any]:
    """Serialize Pydantic models for both v1 and v2 clients."""
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()


async def pipeline_worker(report: RawReport):
    logger.info(f"[Pipeline] Starting pipeline for report {report.report_id}")
    try:
        sync_crisis_event(
            report.report_id,
            raw_text=report.raw_text,
            source=report.source,
            timestamp=report.timestamp.isoformat(),
            status="Pending",
        )

        ingestion_out = await run_ingestion_agent(report)
        sync_crisis_event(
            report.report_id,
            translated_english=ingestion_out.translated_english,
            location_extracted=ingestion_out.location_extracted,
            status="Ingested",
        )
        log_agent_action(
            report.report_id,
            "Ingestion Agent",
            "Processed raw report, translated Roman Urdu and validated location.",
            serialize_model(ingestion_out),
        )

        analysis_out = await run_analysis_agent(ingestion_out)
        sync_crisis_event(
            report.report_id,
            situation_type=analysis_out.situation_type,
            severity=analysis_out.severity,
            confidence=float(analysis_out.confidence),
            impact_details=analysis_out.impact_details,
            status="Analyzed",
        )
        log_agent_action(
            report.report_id,
            "Analysis Agent",
            "Analyzed the situation type, severity, confidence and contextual impact.",
            serialize_model(analysis_out),
        )

        orchestrator_out = await run_orchestrator_agent(analysis_out)
        log_agent_action(
            report.report_id,
            "Orchestrator Agent",
            "Generated recommended response actions based on the analysis output.",
            serialize_model(orchestrator_out),
        )

        simulation_out = await run_simulation_agent(orchestrator_out)
        sync_crisis_event(report.report_id, status="Simulated")
        log_agent_action(
            report.report_id,
            "Simulation Agent",
            "Simulated resolution time, success probability and cascading risks.",
            serialize_model(simulation_out),
        )
        save_simulated_state(
            report.report_id,
            [serialize_model(action) for action in orchestrator_out.recommended_actions],
            {
                "estimated_resolution_time": simulation_out.estimated_resolution_time,
                "cascading_effects": simulation_out.cascading_effects,
                "success_probability": float(simulation_out.success_probability),
            },
        )

        logger.info(f"[Pipeline] Finished pipeline successfully for report {report.report_id}")
    except Exception as exc:
        logger.error(f"[Pipeline] Error running pipeline for report {report.report_id}: {str(exc)}", exc_info=True)
        try:
            sync_crisis_event(report.report_id, status=f"Failed: {str(exc)[:80]}")
        except Exception as db_err:
            logger.error(f"[Pipeline] Failed to update error status in DB: {str(db_err)}")


@router.post("/ingest", status_code=202)
async def ingest_report(report: RawReport, background_tasks: BackgroundTasks):
    background_tasks.add_task(pipeline_worker, report)
    return {
        "status": "Accepted",
        "report_id": report.report_id,
        "message": "Pipeline started in background.",
    }
