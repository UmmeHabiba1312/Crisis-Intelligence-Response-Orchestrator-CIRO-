from fastapi import FastAPI

app = FastAPI(title="CIRO API")

@app.get("/")
def read_root():
    return {"message": "Welcome to CIRO API"}
