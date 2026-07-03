import os
import logging
from supabase import create_client, Client
from dotenv import load_dotenv

# Set up logger
logger = logging.getLogger("uvicorn.error")

# Load environment variables
load_dotenv()

url: str = os.environ.get("SUPABASE_URL", "")
key: str = os.environ.get("SUPABASE_KEY", "")

class MockSupabaseTable:
    def __init__(self, name: str):
        self.name = name

    def insert(self, data):
        logger.info(f"[Mock DB - {self.name}] INSERT: {data}")
        return self

    def upsert(self, data):
        logger.info(f"[Mock DB - {self.name}] UPSERT: {data}")
        return self

    def execute(self):
        return {"data": [], "count": 0}

class MockSupabaseClient:
    def table(self, name: str):
        return MockSupabaseTable(name)

# Initialize client with fallback
if url and key:
    try:
        supabase: Client = create_client(url, key)
        logger.info("[Supabase] Successfully initialized real client.")
    except Exception as e:
        logger.warning(f"[Supabase Warning] Failed to initialize real client: {e}. Using mock client fallback.")
        supabase = MockSupabaseClient()
else:
    logger.warning("[Supabase Warning] SUPABASE_URL or SUPABASE_KEY not set. Using mock client fallback.")
    supabase = MockSupabaseClient()
