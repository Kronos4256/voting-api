from httpx import AsyncClient

from tests.factories import cast_vote, create_candidate, create_voter


async def test_registers_voter_with_normalized_data(client: AsyncClient):
    response = await client.post("/voters", json={"name": "  Ana Torres ", "email": "Ana@Mail.com"})

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Ana Torres"
    assert body["email"] == "ana@mail.com"
    assert body["has_voted"] is False
    assert response.headers["location"].endswith(f"/voters/{body['id']}")


async def test_rejects_duplicated_email_ignoring_case(client: AsyncClient):
    await create_voter(client, email="ana@mail.com")

    response = await client.post("/voters", json={"name": "Otra Ana", "email": "ANA@mail.com"})

    assert response.status_code == 409


async def test_rejects_voter_already_registered_as_candidate(client: AsyncClient):
    await create_candidate(client, email="luis@mail.com")

    response = await client.post("/voters", json={"name": "Luis", "email": "luis@mail.com"})

    assert response.status_code == 409
    assert response.json()["detail"] == "Email is already registered as a candidate"


async def test_validates_payload(client: AsyncClient):
    response = await client.post("/voters", json={"name": "   ", "email": "not-an-email"})

    assert response.status_code == 422


async def test_gets_voter_by_id(client: AsyncClient):
    voter = await create_voter(client)

    response = await client.get(f"/voters/{voter['id']}")

    assert response.status_code == 200
    assert response.json() == voter


async def test_returns_404_for_unknown_voter(client: AsyncClient):
    response = await client.get("/voters/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Voter 999 not found"


async def test_lists_voters_with_pagination_and_filters(client: AsyncClient):
    candidate = await create_candidate(client)
    ana = await create_voter(client, name="Ana Torres")
    await create_voter(client, name="Andrés Ruiz")
    await create_voter(client, name="Carlos Pérez")
    await cast_vote(client, ana["id"], candidate["id"])

    first_page = (await client.get("/voters", params={"size": 2})).json()
    by_name = (await client.get("/voters", params={"name": "an"})).json()
    voted = (await client.get("/voters", params={"has_voted": True})).json()

    assert first_page["total"] == 3
    assert len(first_page["items"]) == 2
    assert {voter["name"] for voter in by_name["items"]} == {"Ana Torres", "Andrés Ruiz"}
    assert [voter["id"] for voter in voted["items"]] == [ana["id"]]


async def test_name_filter_treats_wildcards_literally(client: AsyncClient):
    await create_voter(client, name="Ana Torres")

    response = await client.get("/voters", params={"name": "%"})

    assert response.json()["total"] == 0


async def test_deletes_voter(client: AsyncClient):
    voter = await create_voter(client)

    response = await client.delete(f"/voters/{voter['id']}")

    assert response.status_code == 204
    assert (await client.get(f"/voters/{voter['id']}")).status_code == 404


async def test_refuses_to_delete_voter_who_already_voted(client: AsyncClient):
    voter = await create_voter(client)
    candidate = await create_candidate(client)
    await cast_vote(client, voter["id"], candidate["id"])

    response = await client.delete(f"/voters/{voter['id']}")

    assert response.status_code == 409


async def test_returns_404_when_deleting_unknown_voter(client: AsyncClient):
    response = await client.delete("/voters/999")

    assert response.status_code == 404
