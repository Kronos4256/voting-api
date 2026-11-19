from itertools import count

from httpx import AsyncClient

_sequence = count(1)


async def create_voter(client: AsyncClient, name: str = "Ana Torres", **fields) -> dict:
    payload = {"name": name, "email": f"voter{next(_sequence)}@example.com", **fields}
    response = await client.post("/voters", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


async def create_candidate(client: AsyncClient, name: str = "Luis Gómez", **fields) -> dict:
    payload = {"name": name, "email": f"candidate{next(_sequence)}@example.com", **fields}
    response = await client.post("/candidates", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


async def cast_vote(client: AsyncClient, voter_id: int, candidate_id: int) -> dict:
    response = await client.post(
        "/votes", json={"voter_id": voter_id, "candidate_id": candidate_id}
    )
    assert response.status_code == 201, response.text
    return response.json()
