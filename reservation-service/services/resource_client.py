import os
import httpx
from fastapi import HTTPException


def _get(path: str, label: str):
    base_url = os.getenv("USER_RESOURCE_SERVICE_URL", "http://localhost:8001")
    try:
        response = httpx.get(f"{base_url}{path}", timeout=5)
    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="User & Resource Service indisponible",
        )
    if response.status_code == 404:
        raise HTTPException(status_code=404, detail=f"{label} introuvable")
    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"Réponse inattendue du User & Resource Service ({response.status_code})",
        )
    return response.json()


def check_resource(resource_id: int):
    return _get(f"/resources/{resource_id}", "Ressource")


def check_user(user_id: int):
    return _get(f"/users/{user_id}", "Utilisateur")