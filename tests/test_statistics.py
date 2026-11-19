from httpx import AsyncClient

from tests.factories import cast_vote, create_candidate, create_voter


async def test_statistics_without_votes(client: AsyncClient):
    await create_candidate(client)
    await create_voter(client)

    response = await client.get("/votes/statistics")

    assert response.status_code == 200
    body = response.json()
    assert body["total_votes"] == 0
    assert body["turnout_percentage"] == 0.0
    assert body["results"][0]["percentage"] == 0.0


async def test_statistics_reflect_cast_votes(client: AsyncClient):
    luis = await create_candidate(client, name="Luis", party="Verde")
    marta = await create_candidate(client, name="Marta")
    voters = [await create_voter(client) for _ in range(4)]
    for voter, candidate in zip(voters[:3], (luis, luis, marta), strict=True):
        await cast_vote(client, voter["id"], candidate["id"])

    body = (await client.get("/votes/statistics")).json()

    assert body["total_votes"] == 3
    assert body["voters_who_voted"] == 3
    assert body["total_voters"] == 4
    assert body["turnout_percentage"] == 75.0
    assert body["results"] == [
        {
            "candidate_id": luis["id"],
            "name": "Luis",
            "party": "Verde",
            "votes": 2,
            "percentage": 66.67,
        },
        {
            "candidate_id": marta["id"],
            "name": "Marta",
            "party": None,
            "votes": 1,
            "percentage": 33.33,
        },
    ]
