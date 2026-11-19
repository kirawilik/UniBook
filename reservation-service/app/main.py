from fastapi import FastAPI
from database import engine, Base
from models.reservation import Reservation  # noqa: F401

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Reservation Service")


@app.get("/health")
def health():
    return {"status": "ok"}