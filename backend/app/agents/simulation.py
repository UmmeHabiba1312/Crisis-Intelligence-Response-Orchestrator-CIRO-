import logging
from app.core.schemas import OrchestratorOutput, SimulationOutput
import random

logger = logging.getLogger("uvicorn.error")

async def run_simulation_agent(orchestrator_data: OrchestratorOutput) -> SimulationOutput:
    """
    Simulation Agent logic:
    Predicts resolution outcomes, time, cascading risks, and success probability.
    """
    logger.info(f"[Simulation Agent] Running simulation for report {orchestrator_data.report_id}")
    
    severity = orchestrator_data.analysis_data.severity.lower()
    situation = orchestrator_data.analysis_data.situation_type.lower()
    
    # Estimate resolution time and cascading effects based on severity and situation
    if severity == "critical":
        est_time = "4-8 hours"
        success_prob = 0.75
        if "flood" in situation:
            cascading = "Potential power outages, traffic gridlock in surrounding sectors, and water-borne disease risk."
        elif "fire" in situation:
            cascading = "Risk of structure collapse and toxic smoke spreading to nearby residential zones."
        else:
            cascading = "High risk of localized disruption and strain on emergency services."
    else:
        est_time = "1-3 hours"
        success_prob = 0.95
        cascading = "Minimal cascading risks expected if response is initiated promptly."
        
    # Slightly randomize success probability for realistic simulation variance
    success_prob = max(0.5, min(1.0, success_prob + random.uniform(-0.05, 0.05)))
    
    return SimulationOutput(
        report_id=orchestrator_data.report_id,
        estimated_resolution_time=est_time,
        cascading_effects=cascading,
        success_probability=round(success_prob, 2),
        orchestrator_data=orchestrator_data
    )
