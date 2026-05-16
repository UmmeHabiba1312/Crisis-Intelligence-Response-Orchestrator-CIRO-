from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone

class RawReport(BaseModel):
    report_id: str
    raw_text: str
    source: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class IngestionOutput(BaseModel):
    report_id: str
    raw_text: str
    translated_english: str
    location_extracted: Optional[str] = None
    source: str

class AnalysisOutput(BaseModel):
    report_id: str
    situation_type: str
    severity: str
    confidence: float
    impact_details: Dict[str, Any]
    ingestion_data: IngestionOutput

class Action(BaseModel):
    action_type: str
    target: str
    priority: int

class OrchestratorOutput(BaseModel):
    report_id: str
    recommended_actions: List[Action]
    analysis_data: AnalysisOutput

class SimulationOutput(BaseModel):
    report_id: str
    estimated_resolution_time: str
    cascading_effects: str
    success_probability: float
    orchestrator_data: OrchestratorOutput
