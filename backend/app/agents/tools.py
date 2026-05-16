import random

# --- Ingestion Tools ---
def translate_roman_urdu(text: str) -> str:
    """Mock translation from Roman Urdu to English."""
    lower_text = text.lower()
    if "pani bhar gaya" in lower_text:
        return "Water has flooded, roads are inundated."
    elif "aag" in lower_text:
        return "Fire outbreak reported."
    return "Translated standard text"

def validate_location(location_str: str) -> str:
    """Mock validation for extracting sectors from text."""
    valid_sectors = ["G-10", "F-8", "I-9", "Blue Area", "Kashmir Highway"]
    for sector in valid_sectors:
        if sector.lower() in location_str.lower():
            return sector
    return "Unknown Location"

# --- Analysis Tools ---
def fetch_historical_data(location: str, situation: str) -> dict:
    """Mock retrieving historical data for a location and situation."""
    return {
        "past_incidents": random.randint(1, 10),
        "avg_resolution_time": f"{random.randint(2, 6)} hours"
    }

def weather_api_mock(location: str) -> dict:
    """Mock fetching weather data for context."""
    return {
        "condition": "Heavy Rain", 
        "precipitation": "50mm"
    }
