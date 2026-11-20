from fastapi import FastAPI
from database import engine, Base
from models.reservation import Reservation  # noqa: F401
from routers import reservations

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Reservation Service")
app.include_router(reservations.router)


@app.get("/health")
def health():
    return {"status": "ok"}