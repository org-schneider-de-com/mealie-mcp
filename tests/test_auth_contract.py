"""OIDC token and ASGI authentication boundaries."""

import time

import httpx
import jwt
import pytest

from mealie_mcp.auth import OAuthConfig, extract_bearer_token
from mealie_mcp.server import _BearerAuthMiddleware, _ContentTypeFixMiddleware


@pytest.mark.asyncio
async def test_discovery_is_cached_and_missing_jwks_is_rejected(monkeypatch):
    calls = []

    def handler(request):
        calls.append(str(request.url))
        return httpx.Response(200, json={"issuer": "https://auth.test"})

    original = httpx.AsyncClient
    monkeypatch.setattr(
        httpx, "AsyncClient", lambda **kw: original(transport=httpx.MockTransport(handler))
    )
    config = OAuthConfig("https://auth.test/", "client", "https://mcp.test/")
    assert await config.get_well_known_config() == await config.get_well_known_config()
    assert calls == ["https://auth.test/.well-known/openid-configuration"]
    with pytest.raises(RuntimeError, match="jwks_uri"):
        await config._get_jwk_client()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "claims,accepted",
    [
        ({"iss": "https://auth.test/", "aud": "client", "exp": time.time() + 100}, True),
        (
            {
                "iss": "https://auth.test",
                "aud": ["other", "https://mcp.test"],
                "exp": time.time() + 100,
            },
            True,
        ),
        ({"iss": "https://auth.test", "exp": time.time() + 100}, True),
        ({"iss": "https://wrong.test", "aud": "client", "exp": time.time() + 100}, False),
        ({"iss": "https://auth.test", "aud": "wrong", "exp": time.time() + 100}, False),
        ({"iss": "https://auth.test", "exp": time.time() - 1}, False),
    ],
)
async def test_verified_claims_require_issuer_audience_and_future_expiry(
    monkeypatch, claims, accepted
):
    config = OAuthConfig("https://auth.test/", "client", "https://mcp.test/")

    class Keys:
        def get_signing_key_from_jwt(self, _token):
            return type("Key", (), {"key": "public"})()

    async def get_keys():
        return Keys()

    monkeypatch.setattr(config, "_get_jwk_client", get_keys)
    monkeypatch.setattr(jwt, "decode", lambda *_a, **_kw: claims)
    assert (await config.verify_token("jwt") is not None) is accepted


@pytest.mark.asyncio
async def test_invalid_signature_and_unavailable_key_fail_closed(monkeypatch):
    config = OAuthConfig("https://auth.test", "client", "https://mcp.test")

    async def unavailable():
        raise OSError("JWKS unavailable")

    monkeypatch.setattr(config, "_get_jwk_client", unavailable)
    assert await config.verify_token("bad") is None


@pytest.mark.parametrize(
    "headers,expected",
    [
        ({b"Authorization": b"Bearer abc"}, "abc"),
        ([(b"AUTHORIZATION", b"bearer  abc  ")], "abc"),
        ({b"authorization": b"Basic secret"}, None),
        ({b"authorization": b"Bearer "}, None),
        ({}, None),
    ],
)
def test_extract_bearer_token(headers, expected):
    assert extract_bearer_token(headers) == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "path,token,expected_status",
    [
        ("/mcp", None, 401),
        ("/mcp", "invalid", 401),
        ("/mcp", "valid", 204),
        ("/health", None, 204),
        ("/.well-known/oauth-protected-resource", None, 204),
    ],
)
async def test_protected_paths_reject_missing_or_invalid_tokens(path, token, expected_status):
    async def inner(_scope, _receive, send):
        await send({"type": "http.response.start", "status": 204, "headers": []})
        await send({"type": "http.response.body", "body": b""})

    config = OAuthConfig("https://auth.test", "client", "https://mcp.test/mcp")

    async def verify(value):
        return {"sub": "user"} if value == "valid" else None

    config.verify_token = verify
    messages = []

    async def send(message):
        messages.append(message)

    headers = [(b"authorization", f"Bearer {token}".encode())] if token else []
    await _BearerAuthMiddleware(inner, config)(
        {"type": "http", "path": path, "headers": headers}, lambda: None, send
    )
    assert messages[0]["status"] == expected_status
    if expected_status == 401:
        assert b"resource_metadata" in dict(messages[0]["headers"])[b"www-authenticate"]


@pytest.mark.asyncio
async def test_content_type_middleware_rewrites_probe_and_replays_real_body():
    received = []

    async def inner(scope, receive, send):
        received.append((scope["headers"], await receive()))
        await send({"type": "http.response.start", "status": 204, "headers": []})

    middleware = _ContentTypeFixMiddleware(inner)
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/mcp",
        "headers": [(b"content-type", b"application/octet-stream")],
    }
    messages = []

    async def send(message):
        messages.append(message)

    async def empty_body():
        return {"type": "http.request", "body": b""}

    async def real_body():
        return {"type": "http.request", "body": b"{}"}

    await middleware(scope, empty_body, send)
    assert messages[0]["status"] == 200
    assert not received
    await middleware(scope, real_body, send)
    assert received[0][1]["body"] == b"{}"
    assert (b"content-type", b"application/json") in received[0][0]
