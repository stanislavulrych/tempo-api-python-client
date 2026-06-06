import httpx

from tempoapi import Client_v4


def test_get_accounts_sends_bearer_auth() -> None:
    seen_auth = ""

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal seen_auth
        seen_auth = request.headers.get("authorization", "")
        return httpx.Response(200, json={"results": [{"id": "1", "key": "ACC"}], "metadata": {}})

    transport = httpx.MockTransport(handler)
    with Client_v4(auth_token="secret-token") as client:
        client._client = httpx.Client(
            transport=transport,
            headers={"Authorization": "Bearer secret-token"},
        )
        result = client.get_accounts()
    assert result == [{"id": "1", "key": "ACC"}]
    assert seen_auth == "Bearer secret-token"


def test_context_manager_closes_client() -> None:
    client = Client_v4(auth_token="t")
    with client:
        assert client._client is not None
    assert client._client is None


def test_ready_without_context_manager() -> None:
    client = Client_v4(auth_token="t")
    assert client._client is not None
    client.close()
    assert client._client is None
