USER = {
    "full_name": "Ahmed Benali",
    "email": "ahmed@univ.dz",
    "password": "secret123",
    "role": "Student",
}


def create_user(client, **overrides):
    """fonction cree un user"""
    return client.post("/users", json={**USER, **overrides})


# ---------- Création ----------
def test_create_user_ok(client):
    r = create_user(client)
    assert r.status_code == 201
    data = r.json()
    assert data["id"] == 1
    assert data["email"] == "ahmed@univ.dz"
    assert data["role"] == "Student"
    assert data["is_active"] is True


def test_password_is_hashed_in_db(client, db):
    from app.models import User

    create_user(client)
    user = db.get(User, 1)
    assert user.password_hash != "secret123"
    assert user.password_hash.startswith("$2b$")   # bcrypt

def test_password_hash_not_exposed(client):
    r = create_user(client)
    assert "password" not in r.json()
    assert "password_hash" not in r.json()


def test_create_user_duplicate_email(client):
    create_user(client)
    r = create_user(client, full_name="Autre Personne")
    assert r.status_code == 409


def test_create_user_invalid_role(client):
    r = create_user(client, role="Boss")
    assert r.status_code == 422


def test_create_user_invalid_email(client):
    r = create_user(client, email="abc")
    assert r.status_code == 422


def test_create_user_short_password(client):
    r = create_user(client, password="123")
    assert r.status_code == 422


def test_create_user_missing_field(client):
    payload = {k: v for k, v in USER.items() if k != "full_name"}
    r = client.post("/users", json=payload)
    assert r.status_code == 422


# ---------- Lecture ----------
def test_get_user_by_id(client):
    create_user(client)
    r = client.get("/users/1")
    assert r.status_code == 200
    assert r.json()["full_name"] == "Ahmed Benali"


def test_get_user_not_found(client):
    assert client.get("/users/999").status_code == 404


def test_list_users_empty(client):
    r = client.get("/users")
    assert r.status_code == 200
    assert r.json() == []


def test_list_users(client):
    create_user(client, email="a@univ.dz")
    create_user(client, email="b@univ.dz")
    r = client.get("/users")
    assert r.status_code == 200
    assert len(r.json()) == 2


# ---------- Modification ----------
def test_update_user(client):
    create_user(client)
    r = client.put("/users/1", json={"full_name": "Ahmed B.", "role": "Teacher"})
    assert r.status_code == 200
    assert r.json()["full_name"] == "Ahmed B."
    assert r.json()["role"] == "Teacher"
    assert r.json()["email"] == "ahmed@univ.dz"   # ما تبدّلش


def test_update_user_password_is_rehashed(client, db):
    from app.models import User
    from app.services.security import verify_password

    create_user(client)
    assert client.put("/users/1", json={"password": "newpass456"}).status_code == 200

    user = db.get(User, 1)
    assert verify_password("newpass456", user.password_hash)
    assert not verify_password("secret123", user.password_hash)


def test_update_user_duplicate_email(client):
    create_user(client, email="a@univ.dz")
    create_user(client, email="b@univ.dz")
    r = client.put("/users/2", json={"email": "a@univ.dz"})
    assert r.status_code == 409


def test_update_user_not_found(client):
    r = client.put("/users/999", json={"full_name": "X Y"})
    assert r.status_code == 404


# ---------- Désactivation (soft delete) ----------
def test_delete_user_is_soft(client):
    create_user(client)
    assert client.delete("/users/1").status_code == 204

    r = client.get("/users/1")
    assert r.status_code == 200
    assert r.json()["is_active"] is False


def test_delete_user_not_found(client):
    assert client.delete("/users/999").status_code == 404