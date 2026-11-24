import pytest
from pydantic import ValidationError

from app.schemas import ReservationEvent
from app.services.notification_service import process_event

CREATED = {
    "event_type": "ReservationCreated",
    "reservation_id": 12,
    "user_id": 1,
    "resource_id": 1,
    "date": "2026-12-01",
    "start_time": "09:00:00",
    "end_time": "11:00:00",
    "created_at": "2026-11-23T10:00:00",
}


def make_event(**overrides):
    return ReservationEvent(**{**CREATED, **overrides})


# ---------- Contrat (schéma d'événement) ----------
def test_event_valid():
    assert make_event().reservation_id == 12


def test_event_unknown_type_rejected():
    with pytest.raises(ValidationError):
        make_event(event_type="ReservationDeleted")


def test_event_missing_field_rejected():
    payload = {k: v for k, v in CREATED.items() if k != "user_id"}
    with pytest.raises(ValidationError):
        ReservationEvent(**payload)


# ---------- process_event ----------
def test_process_created_event(db):
    n = process_event(db, make_event())
    assert n.id == 1
    assert n.status == "Sent"
    assert "créée" in n.message
    assert "09:00" in n.message and "11:00" in n.message


def test_process_cancelled_event(db):
    n = process_event(db, make_event(event_type="ReservationCancelled",
                                     cancelled_at="2026-11-24T08:30:00"))
    assert "annulée" in n.message


def test_duplicate_event_is_not_saved_twice(db):
    first = process_event(db, make_event())
    second = process_event(db, make_event())
    assert first.id == second.id


def test_created_and_cancelled_are_two_notifications(db):
    a = process_event(db, make_event())
    b = process_event(db, make_event(event_type="ReservationCancelled"))
    assert a.id != b.id


# ---------- API ----------
def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_list_empty(client):
    r = client.get("/notifications")
    assert r.status_code == 200
    assert r.json() == []


def test_list_notifications(client, db):
    process_event(db, make_event(reservation_id=1))
    process_event(db, make_event(reservation_id=2))
    r = client.get("/notifications")
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_filter_by_user(client, db):
    process_event(db, make_event(reservation_id=1, user_id=1))
    process_event(db, make_event(reservation_id=2, user_id=2))
    r = client.get("/notifications", params={"user_id": 2})
    assert len(r.json()) == 1
    assert r.json()[0]["user_id"] == 2


def test_get_notification_by_id(client, db):
    process_event(db, make_event())
    r = client.get("/notifications/1")
    assert r.status_code == 200
    assert r.json()["reservation_id"] == 12


def test_get_notification_not_found(client):
    assert client.get("/notifications/999").status_code == 404