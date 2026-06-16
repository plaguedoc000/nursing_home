from fastapi import FastAPI

from app.routers import pansionats, room_types, rooms

app = FastAPI(title="Nursing Home API", version="1.0.0")

app.include_router(pansionats.router)
app.include_router(room_types.router)
app.include_router(rooms.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
