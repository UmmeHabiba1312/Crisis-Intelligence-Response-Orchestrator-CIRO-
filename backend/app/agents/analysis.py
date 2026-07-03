import logging
from app.core.schemas import IngestionOutput, AnalysisOutput
from app.agents.tools import fetch_historical_data, weather_api_mock

logger = logging.getLogger("uvicorn.error")

async def run_analysis_agent(ingestion_data: IngestionOutput) -> AnalysisOutput:
    """
    Analysis Agent logic:
    Determines severity, entity extraction, and evaluates confidence.
    """
    logger.info(f"[Analysis Agent] Analyzing report {ingestion_data.report_id}")
    
    # Determine Situation & Severity
    situation_type = "General Incident"
    severity = "Low"
    
    text_to_analyze = ingestion_data.translated_english.lower()
    if "flood" in text_to_analyze or "water" in text_to_analyze:
        situation_type = "Urban Flooding"
        severity = "Critical"
    elif "fire" in text_to_analyze:
        situation_type = "Fire Outbreak"
        severity = "Critical"
    
    # Use Tools
    loc = ingestion_data.location_extracted or "Unknown"
    historical = fetch_historical_data(loc, situation_type)
    weather = weather_api_mock(loc)
    
    # Confidence Calculation 
    confidence = 0.85
    if weather["condition"] == "Heavy Rain" and situation_type == "Urban Flooding":
        confidence += 0.10 # Boost confidence based on weather context
        
    impact_details = {
        "weather_context": weather,
        "historical_context": historical,
        "infrastructure_damage": "Likely Road Blockages" if severity == "Critical" else "Minimal"
    }
    
    return AnalysisOutput(
        report_id=ingestion_data.report_id,
        situation_type=situation_type,
        severity=severity,
        confidence=min(1.0, confidence),
        impact_details=impact_details,
        ingestion_data=ingestion_data
    )
