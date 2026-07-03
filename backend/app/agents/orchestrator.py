import logging
from app.core.schemas import AnalysisOutput, OrchestratorOutput, Action
from typing import List

logger = logging.getLogger("uvicorn.error")

async def run_orchestrator_agent(analysis_data: AnalysisOutput) -> OrchestratorOutput:
    """
    Orchestrator Agent logic:
    Recommends response actions based on the situation type and severity.
    """
    logger.info(f"[Orchestrator Agent] Determining actions for report {analysis_data.report_id}")
    
    actions: List[Action] = []
    
    situation = analysis_data.situation_type.lower()
    severity = analysis_data.severity.lower()
    
    if "flood" in situation:
        if severity == "critical":
            actions.append(Action(action_type="Dispatch Rescue Boats", target="Flooded Areas", priority=1))
            actions.append(Action(action_type="Issue Evacuation Order", target="Low-lying Sectors", priority=2))
        else:
            actions.append(Action(action_type="Monitor Water Levels", target="Drainage Channels", priority=3))
    elif "fire" in situation:
        if severity == "critical":
            actions.append(Action(action_type="Dispatch Fire Engines", target="Affected Structure", priority=1))
            actions.append(Action(action_type="Evacuate Adjacent Buildings", target="Immediate Vicinity", priority=2))
        else:
            actions.append(Action(action_type="Send Local Response Team", target="Incident Site", priority=3))
    else:
        # Default action
        actions.append(Action(action_type="Deploy Assessment Team", target="Reported Location", priority=3))
        
    return OrchestratorOutput(
        report_id=analysis_data.report_id,
        recommended_actions=actions,
        analysis_data=analysis_data
    )
