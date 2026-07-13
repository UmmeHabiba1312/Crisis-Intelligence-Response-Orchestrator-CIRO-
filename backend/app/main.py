from fastapi import FastAPI

from app.core.db import initialize_database
from app.routes.reports import router as reports_router

app = FastAPI(title="CIRO API")

app.include_router(reports_router, tags=["Reports"])


@app.on_event("startup")
def startup_event():
    initialize_database()


@app.get("/")
def read_root():
    return {"message": "Welcome to CIRO API"}
