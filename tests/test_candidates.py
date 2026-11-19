import asyncio

from httpx import AsyncClient

from tests.factories import cast_vote, create_candidate, create_voter


async def test_registers_candidate(client: AsyncClient):
    response = await client.post(
        "/candidates", json={"name": "Luis Gómez", "email": "luis@mail.com", "party": "Verde"}
    )

    assert response.status_code == 201
    body = response.json()
    assert body["party"] == "Verde"
    assert body["votes"] == 0
    assert response.headers["location"].endswith(f"/candidates/{body['id']}")


async def test_party_is_optional(client: AsyncClient):
    candidate = await create_candidate(client)

    assert candidate["party"] is None


async def test_rejects_candidate_already_registered_as_voter(client: AsyncClient):
    await create_voter(client, email="ana@mail.com")

    response = await client.post("/candidates", json={"name": "Ana", "email": "ana@mail.com"})

    assert response.status_code == 409
    assert response.json()["detail"] == "Email is already registered as a voter"


async def test_lists_candidates_filtered_by_party(client: AsyncClient):
    await create_candidate(client, name="Luis", party="Partido Verde")
    await create_candidate(client, name="Marta", party="Partido Azul")
    await create_candidate(client, name="Sofía")

    response = await client.get("/candidates", params={"party": "verde"})

    assert [candidate["name"] for candidate in response.json()["items"]] == ["Luis"]


async def test_returns_404_for_unknown_candidate(client: AsyncClient):
    response = await client.get("/candidates/999")

    assert response.status_code == 404


async def test_deletes_candidate_without_votes(client: AsyncClient):
    candidate = await create_candidate(client)

    response = await client.delete(f"/candidates/{candidate['id']}")

    assert response.status_code == 204


async def test_refuses_to_delete_candidate_with_votes(client: AsyncClient):
    voter = await create_voter(client)
    candidate = await create_candidate(client)
    await cast_vote(client, voter["id"], candidate["id"])

    response = await client.delete(f"/candidates/{candidate['id']}")

    assert response.status_code == 409


async def test_same_email_cannot_register_as_voter_and_candidate_concurrently(
    client: AsyncClient,
):
    payload = {"name": "Ana", "email": "ana@mail.com"}

    responses = await asyncio.gather(
        *(client.post(path, json=payload) for path in ("/voters", "/candidates") * 3)
    )

    assert sorted(response.status_code for response in responses) == [201, 409, 409, 409, 409, 409]
