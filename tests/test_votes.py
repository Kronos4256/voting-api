import asyncio

from httpx import AsyncClient

from tests.factories import cast_vote, create_candidate, create_voter


async def test_vote_marks_voter_and_counts_for_candidate(client: AsyncClient):
    voter = await create_voter(client)
    candidate = await create_candidate(client)

    response = await client.post(
        "/votes", json={"voter_id": voter["id"], "candidate_id": candidate["id"]}
    )

    assert response.status_code == 201
    assert response.json()["voter_id"] == voter["id"]
    assert (await client.get(f"/voters/{voter['id']}")).json()["has_voted"] is True
    assert (await client.get(f"/candidates/{candidate['id']}")).json()["votes"] == 1


async def test_voter_cannot_vote_twice(client: AsyncClient):
    voter = await create_voter(client)
    first = await create_candidate(client)
    second = await create_candidate(client)
    await cast_vote(client, voter["id"], first["id"])

    response = await client.post(
        "/votes", json={"voter_id": voter["id"], "candidate_id": second["id"]}
    )

    assert response.status_code == 409
    assert (await client.get(f"/candidates/{second['id']}")).json()["votes"] == 0


async def test_concurrent_votes_from_same_voter_count_once(client: AsyncClient):
    voter = await create_voter(client)
    candidate = await create_candidate(client)
    payload = {"voter_id": voter["id"], "candidate_id": candidate["id"]}

    responses = await asyncio.gather(*(client.post("/votes", json=payload) for _ in range(5)))

    assert sorted(response.status_code for response in responses) == [201, 409, 409, 409, 409]
    assert (await client.get(f"/candidates/{candidate['id']}")).json()["votes"] == 1
    assert (await client.get("/votes")).json()["total"] == 1


async def test_unknown_candidate_leaves_voter_untouched(client: AsyncClient):
    voter = await create_voter(client)

    response = await client.post("/votes", json={"voter_id": voter["id"], "candidate_id": 999})

    assert response.status_code == 404
    assert response.json()["detail"] == "Candidate 999 not found"
    assert (await client.get(f"/voters/{voter['id']}")).json()["has_voted"] is False


async def test_unknown_voter_is_rejected(client: AsyncClient):
    candidate = await create_candidate(client)

    response = await client.post("/votes", json={"voter_id": 999, "candidate_id": candidate["id"]})

    assert response.status_code == 404
    assert response.json()["detail"] == "Voter 999 not found"


async def test_lists_votes(client: AsyncClient):
    candidate = await create_candidate(client)
    for _ in range(3):
        voter = await create_voter(client)
        await cast_vote(client, voter["id"], candidate["id"])

    response = await client.get("/votes", params={"page": 2, "size": 2})

    body = response.json()
    assert body["total"] == 3
    assert len(body["items"]) == 1
