import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from database import Base, get_db
from services import reservation_service

engine = create_engine(
    "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
)
TestingSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture(autouse=True)
def setup(monkeypatch):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    monkeypatch.setattr(reservation_service, "check_user", lambda uid: {"id": uid})
    monkeypatch.setattr(reservation_service, "check_resource", lambda rid: {"id": rid})
    yield
    app.dependency_overrides.clear()


client = TestClient(app)

BODY = {"user_id": 1, "resource_id": 1, "date": "2026-12-01",
        "start_time": "09:00:00", "end_time": "11:00:00"}


def test_create_reservation():
    r = client.post("/reservations", json=BODY)
    assert r.status_code == 201
    assert r.json()["status"] == "CONFIRMED"


def test_conflict_returns_409():
    client.post("/reservations", json=BODY)
    r = client.post("/reservations", json={**BODY, "start_time": "10:00:00", "end_time": "12:00:00"})
    assert r.status_code == 409


def test_adjacent_slots_are_allowed():
    client.post("/reservations", json=BODY)
    r = client.post("/reservations", json={**BODY, "start_time": "11:00:00", "end_time": "12:00:00"})
    assert r.status_code == 201


def test_invalid_time_range():
    r = client.post("/reservations", json={**BODY, "start_time": "12:00:00", "end_time": "10:00:00"})
    assert r.status_code == 422


def test_cancel_frees_slot():
    rid = client.post("/reservations", json=BODY).json()["id"]
    assert client.patch(f"/reservations/{rid}/cancel").status_code == 200
    assert client.post("/reservations", json=BODY).status_code == 201


def test_history_by_user():
    client.post("/reservations", json=BODY)
    r = client.get("/reservations", params={"user_id": 1})
    assert r.status_code == 200
    assert len(r.json()) == 1