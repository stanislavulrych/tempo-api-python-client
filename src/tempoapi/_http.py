from typing import Any

import httpx

DEFAULT_TIMEOUT = 75.0
JSON_HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}


def url_joiner(base_url: str, path: str) -> str:
    if path.startswith("https://"):
        return path
    return "/".join(s.strip("/") for s in [base_url, path])


def raise_for_status(response: httpx.Response, url: str) -> None:
    if response.is_success:
        return
    body = (response.text or "").strip()[:2000]
    raise httpx.HTTPStatusError(
        f"HTTP {response.status_code} {response.reason_phrase} for {url}: {body or '(empty body)'}",
        request=response.request,
        response=response,
    )


def parse_json(response: httpx.Response) -> Any:
    if not response.text:
        return {}
    return response.json()


async def request_json(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    **kwargs: Any,
) -> Any:
    response = await client.request(method, url, **kwargs)
    raise_for_status(response, url)
    return parse_json(response)


def request_json_sync(
    client: httpx.Client,
    method: str,
    url: str,
    **kwargs: Any,
) -> Any:
    response = client.request(method, url, **kwargs)
    raise_for_status(response, url)
    return parse_json(response)


def create_tempo_client(
    auth_token: str,
    *,
    timeout: float = DEFAULT_TIMEOUT,
) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        headers={**JSON_HEADERS, "Authorization": f"Bearer {auth_token}"},
        timeout=timeout,
    )


def create_tempo_sync_client(
    auth_token: str,
    *,
    timeout: float = DEFAULT_TIMEOUT,
) -> httpx.Client:
    return httpx.Client(
        headers={**JSON_HEADERS, "Authorization": f"Bearer {auth_token}"},
        timeout=timeout,
    )
