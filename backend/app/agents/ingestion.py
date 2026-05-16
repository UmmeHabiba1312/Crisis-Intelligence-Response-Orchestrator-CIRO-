from app.core.schemas import RawReport, IngestionOutput
from app.agents.tools import translate_roman_urdu, validate_location

async def run_ingestion_agent(report: RawReport) -> IngestionOutput:
    """
    Ingestion Agent logic:
    Normalizes text, translates Roman Urdu, and extracts locations.
    """
    print(f"[Ingestion Agent] Processing report {report.report_id}")
    
    # Utilize tools
    translated_text = translate_roman_urdu(report.raw_text)
    
    # We pass the raw text to location validation here (could also be translated text)
    extracted_loc = validate_location(report.raw_text)
    if extracted_loc == "Unknown Location":
        extracted_loc = None
        
    return IngestionOutput(
        report_id=report.report_id,
        raw_text=report.raw_text,
        translated_english=translated_text,
        location_extracted=extracted_loc,
        source=report.source
    )
