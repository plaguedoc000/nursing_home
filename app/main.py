from fastapi import FastAPI

app = FastAPI(title="Nursing Home API", version="1.0.0")


@app.get("/health")
def health_check():
    return {"status": "ok"}
