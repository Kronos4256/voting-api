from httpx import AsyncClient


async def test_issues_token_for_valid_credentials(anonymous_client: AsyncClient):
    response = await anonymous_client.post(
        "/auth/token", data={"username": "admin", "password": "admin"}
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"


async def test_rejects_invalid_credentials(anonymous_client: AsyncClient):
    response = await anonymous_client.post(
        "/auth/token", data={"username": "admin", "password": "wrong"}
    )

    assert response.status_code == 401


async def test_protected_endpoints_require_token(anonymous_client: AsyncClient):
    for path in ("/voters", "/candidates", "/votes", "/votes/statistics"):
        response = await anonymous_client.get(path)
        assert response.status_code == 401, path


async def test_rejects_tampered_token(anonymous_client: AsyncClient):
    response = await anonymous_client.get(
        "/voters", headers={"Authorization": "Bearer not-a-real-token"}
    )

    assert response.status_code == 401
