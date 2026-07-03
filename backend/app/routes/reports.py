from fastapi import APIRouter, BackgroundTasks
import logging
from app.core.schemas import RawReport
from app.agents.ingestion import run_ingestion_agent
from app.agents.analysis import run_analysis_agent
from app.agents.orchestrator import run_orchestrator_agent
from app.agents.simulation import run_simulation_agent
from app.core.db import supabase

router = APIRouter()
logger = logging.getLogger("uvicorn.error")

def serialize_model(model):
    """Helper to serialize Pydantic models for both v1 and v2."""
    if hasattr(model, "model_dump"):
        return model.model_dump()
    return model.dict()

async def pipeline_worker(report: RawReport):
    logger.info(f"[Pipeline] Starting pipeline for report {report.report_id}")
    try:
        # 1. Ingestion Stage
        ingestion_out = await run_ingestion_agent(report)
        
        # Sync ingestion to Supabase (Initial insert/upsert)
        crisis_data = {
            "report_id": report.report_id,
            "raw_text": report.raw_text,
            "source": report.source,
            "translated_english": ingestion_out.translated_english,
            "location_extracted": ingestion_out.location_extracted,
            "status": "Ingested"
        }
        supabase.table("crisis_events").upsert(crisis_data).execute()
        
        # Log Ingestion Agent action
        supabase.table("agent_logs").insert({
            "report_id": report.report_id,
            "agent_name": "Ingestion Agent",
            "action_taken": "Processed raw report, translated Roman Urdu and validated location.",
            "payload": serialize_model(ingestion_out)
        }).execute()
        
        # 2. Analysis Stage
        analysis_out = await run_analysis_agent(ingestion_out)
        
        # Update crisis_events with analysis results
        analysis_data = {
            "report_id": report.report_id,
            "situation_type": analysis_out.situation_type,
            "severity": analysis_out.severity,
            "confidence": float(analysis_out.confidence),
            "impact_details": analysis_out.impact_details,
            "status": "Analyzed"
        }
        supabase.table("crisis_events").upsert(analysis_data).execute()
        
        # Log Analysis Agent action
        supabase.table("agent_logs").insert({
            "report_id": report.report_id,
            "agent_name": "Analysis Agent",
            "action_taken": "Analyzed situation type, severity, confidence, and context.",
            "payload": serialize_model(analysis_out)
        }).execute()
        
        # 3. Orchestration Stage
        orchestrator_out = await run_orchestrator_agent(analysis_out)
        
        # Log Orchestrator Agent action
        supabase.table("agent_logs").insert({
            "report_id": report.report_id,
            "agent_name": "Orchestrator Agent",
            "action_taken": "Generated recommended actions based on critical assessment.",
            "payload": serialize_model(orchestrator_out)
        }).execute()
        
        # 4. Simulation Stage
        simulation_out = await run_simulation_agent(orchestrator_out)
        
        # Final update to crisis_events
        supabase.table("crisis_events").upsert({
            "report_id": report.report_id,
            "status": "Simulated"
        }).execute()
        
        # Log Simulation Agent action
        supabase.table("agent_logs").insert({
            "report_id": report.report_id,
            "agent_name": "Simulation Agent",
            "action_taken": "Simulated resolution time, success probability, and cascading risks.",
            "payload": serialize_model(simulation_out)
        }).execute()
        
        # Insert simulated state details
        state_data = {
            "report_id": report.report_id,
            "recommended_actions": [serialize_model(a) for a in orchestrator_out.recommended_actions],
            "simulated_outcome": {
                "estimated_resolution_time": simulation_out.estimated_resolution_time,
                "cascading_effects": simulation_out.cascading_effects,
                "success_probability": float(simulation_out.success_probability)
            }
        }
        supabase.table("simulated_states").insert(state_data).execute()
        
        logger.info(f"[Pipeline] Finished pipeline successfully for report {report.report_id}")
        
    except Exception as e:
        logger.error(f"[Pipeline] Error running pipeline for report {report.report_id}: {str(e)}", exc_info=True)
        # Log failure if we got past the initial event creation
        try:
            supabase.table("crisis_events").upsert({
                "report_id": report.report_id,
                "status": f"Failed: {str(e)[:40]}"
            }).execute()
        except Exception as db_err:
            logger.error(f"[Pipeline] Failed to update error status in DB: {str(db_err)}")

@router.post("/ingest", status_code=202)
async def ingest_report(report: RawReport, background_tasks: BackgroundTasks):
    background_tasks.add_task(pipeline_worker, report)
    return {
        "status": "Accepted",
        "report_id": report.report_id,
        "message": "Pipeline started in background."
    }
