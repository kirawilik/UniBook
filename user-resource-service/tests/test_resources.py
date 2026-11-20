import pytest

RESOURCE = {
    "name": "Salle A101",
    "type": "Classroom",
    "description": "Salle avec projecteur",
    "location": "Bâtiment A, 1er étage",
    "capacity": 40,
}


def create_resource(client, **overrides):
    """fonction aider"""
    return client.post("/resources", json={**RESOURCE, **overrides})


# ---------- Création ----------
def test_create_resource_ok(client):
    r = create_resource(client)
    assert r.status_code == 201
    data = r.json()
    assert data["id"] == 1
    assert data["name"] == "Salle A101"
    assert data["is_active"] is True


def test_create_resource_without_optional_fields(client):
    r = client.post("/resources", json={
        "name": "Projecteur P1",
        "type": "Equipment",
        "location": "Magasin",
    })
    assert r.status_code == 201
    assert r.json()["description"] is None
    assert r.json()["capacity"] is None


def test_create_resource_invalid_type(client):
    r = create_resource(client, type="Garage")
    assert r.status_code == 422


def test_create_resource_negative_capacity(client):
    r = create_resource(client, capacity=-5)
    assert r.status_code == 422


def test_create_resource_missing_name(client):
    payload = {k: v for k, v in RESOURCE.items() if k != "name"}
    r = client.post("/resources", json=payload)
    assert r.status_code == 422


# ---------- Lecture ----------
def test_get_resource_by_id(client):
    create_resource(client)
    r = client.get("/resources/1")
    assert r.status_code == 200
    assert r.json()["name"] == "Salle A101"


def test_get_resource_not_found(client):
    r = client.get("/resources/999")
    assert r.status_code == 404


def test_list_resources_empty(client):
    r = client.get("/resources")
    assert r.status_code == 200
    assert r.json() == []


def test_list_resources(client):
    create_resource(client, name="Salle A101")
    create_resource(client, name="Salle A102")
    r = client.get("/resources")
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_filter_resources_by_type(client):
    create_resource(client, name="Salle A101", type="Classroom")
    create_resource(client, name="Labo Info 1", type="Laboratory")
    r = client.get("/resources", params={"type": "Laboratory"})
    assert r.status_code == 200
    assert len(r.json()) == 1
    assert r.json()[0]["name"] == "Labo Info 1"


def test_pagination(client):
    for i in range(5):
        create_resource(client, name=f"Salle {i}")
    r = client.get("/resources", params={"skip": 2, "limit": 2})
    assert r.status_code == 200
    assert len(r.json()) == 2


# ---------- Modification ----------
def test_update_resource(client):
    create_resource(client)
    r = client.put("/resources/1", json={"name": "Salle B202", "capacity": 60})
    assert r.status_code == 200
    assert r.json()["name"] == "Salle B202"
    assert r.json()["capacity"] == 60
    assert r.json()["location"] == "Bâtiment A, 1er étage"   # ما تبدّلش


def test_update_resource_not_found(client):
    r = client.put("/resources/999", json={"name": "X Y"})
    assert r.status_code == 404


# ---------- Désactivation (soft delete) ----------
def test_delete_resource_is_soft(client):
    create_resource(client)
    assert client.delete("/resources/1").status_code == 204

    assert client.get("/resources").json() == []

    r = client.get("/resources", params={"only_active": False})
    assert len(r.json()) == 1
    assert r.json()[0]["is_active"] is False

    assert client.get("/resources/1").json()["is_active"] is False


def test_delete_resource_not_found(client):
    r = client.delete("/resources/999")
    assert r.status_code == 404