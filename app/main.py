from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.routers import pansionats, room_types, rooms, beds, residents, bookings

app = FastAPI(title="Nursing Home API", version="1.0.0")

# TODO: ограничить origins в проде, сейчас разрешено всё
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(pansionats.router)
app.include_router(room_types.router)
app.include_router(rooms.router)
app.include_router(beds.router)
app.include_router(residents.router)
app.include_router(bookings.router)


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/health")
def health_check():
    return {"status": "ok"}
