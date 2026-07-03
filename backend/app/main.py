from fastapi import FastAPI
from app.routes.reports import router as reports_router

app = FastAPI(title="CIRO API")

app.include_router(reports_router, prefix="/report", tags=["Reports"])

@app.get("/")
def read_root():
    return {"message": "Welcome to CIRO API"}
