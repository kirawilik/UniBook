def test_create_resource(client):
    response = client.post("/resources", json={
        "name": "Salle A101",
        "type": "Classroom",
        "description": "Salle avec projecteur",
        "location": "Bâtiment A, 1er étage",
        "capacity": 40,
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Salle A101"
    assert data["is_active"] is True
    assert "created_at" in data