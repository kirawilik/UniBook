from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Notification  # noqa: F401

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)


@event.listens_for(engine, "connect")
def register_sysdatetime(dbapi_connection, _record):
    dbapi_connection.create_function(
        "sysdatetime", 0, lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    )


TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture()
def client():
    Base.metadata.create_all(engine)

    def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)


@pytest.fixture()
def db(client):
    session = TestingSessionLocal()
    yield session
    session.close()