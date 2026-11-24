from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers import notifications


@asynccontextmanager
async def lifespan(app: FastAPI):


# membre b ajouter leur travaille 

    yield


app = FastAPI(title="UniBook - Notification Service", lifespan=lifespan)
app.include_router(notifications.router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/db")
def health_db(db: Session = Depends(get_db)):
    return {"status": "connecté", "version": db.execute(text("SELECT @@VERSION")).scalar()}