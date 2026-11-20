from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.routers import users, resources

app = FastAPI(title="User & Resource Service")
app.include_router(users.router)
app.include_router(resources.router)


@app.get("/health/db")
def test_db(db: Session = Depends(get_db)):
    return {"status": "connecté", "version": db.execute(text("SELECT @@VERSION")).scalar()}