import httpx
import pytest

from tempoapi import AsyncClient_v4


@pytest.mark.asyncio
async def test_get_accounts_sends_bearer_auth() -> None:
    seen_auth = ""

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal seen_auth
        seen_auth = request.headers.get("authorization", "")
        return httpx.Response(200, json={"results": [{"id": "1", "key": "ACC"}], "metadata": {}})

    transport = httpx.MockTransport(handler)
    async with AsyncClient_v4(auth_token="secret-token") as client:
        client._client = httpx.AsyncClient(
            transport=transport,
            headers={"Authorization": "Bearer secret-token"},
        )
        result = await client.get_accounts()
    assert result == [{"id": "1", "key": "ACC"}]
    assert seen_auth == "Bearer secret-token"


@pytest.mark.asyncio
async def test_get_follows_pagination() -> None:
    calls = 0

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            return httpx.Response(
                200,
                json={
                    "results": [{"id": "1"}],
                    "metadata": {"next": "https://api.tempo.io/4/accounts?offset=1"},
                },
            )
        return httpx.Response(200, json={"results": [{"id": "2"}], "metadata": {}})

    transport = httpx.MockTransport(handler)
    async with AsyncClient_v4(auth_token="t") as client:
        client._client = httpx.AsyncClient(transport=transport)
        result = await client.get("/accounts")
    assert result == [{"id": "1"}, {"id": "2"}]
    assert calls == 2


@pytest.mark.asyncio
async def test_context_manager_closes_client() -> None:
    client = AsyncClient_v4(auth_token="t")
    async with client:
        assert client._client is not None
    assert client._client is None
