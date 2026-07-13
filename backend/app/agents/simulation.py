import logging

from app.core.schemas import OrchestratorOutput, SimulationOutput

logger = logging.getLogger("uvicorn.error")


async def run_simulation_agent(orchestrator_data: OrchestratorOutput) -> SimulationOutput:
    """Estimate the likely outcome of the recommended response strategy."""
    logger.info(f"[Simulation Agent] Running simulation for report {orchestrator_data.report_id}")

    severity = (orchestrator_data.analysis_data.severity or "low").lower()
    situation = (orchestrator_data.analysis_data.situation_type or "general incident").lower()

    if severity == "critical":
        est_time = "4-8 hours"
        success_prob = 0.78
        if "flood" in situation:
            cascading = "Potential power outages, traffic gridlock in surrounding sectors, and water-borne disease risk."
        elif "fire" in situation:
            cascading = "Risk of structure collapse and toxic smoke spreading to nearby residential zones."
        else:
            cascading = "High risk of localized disruption and strain on emergency services."
    else:
        est_time = "1-3 hours"
        success_prob = 0.92
        cascading = "Minimal cascading risks expected if response is initiated promptly."

    return SimulationOutput(
        report_id=orchestrator_data.report_id,
        estimated_resolution_time=est_time,
        cascading_effects=cascading,
        success_probability=round(success_prob, 2),
        orchestrator_data=orchestrator_data,
    )
