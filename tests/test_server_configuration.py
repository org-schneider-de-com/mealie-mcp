"""Server configuration must fail clearly and expose correct OAuth discovery."""

import pytest

from mealie_mcp import server


def test_settings_require_mealie_url_and_token(monkeypatch):
    monkeypatch.delenv("MEALIE_URL", raising=False)
    monkeypatch.delenv("MEALIE_API_TOKEN", raising=False)
    with pytest.raises(RuntimeError, match="MEALIE_URL"):
        server._load_settings()
    monkeypatch.setenv("MEALIE_URL", "https://mealie.test")
    with pytest.raises(RuntimeError, match="MEALIE_API_TOKEN"):
        server._load_settings()


def test_oauth_configuration_requires_complete_triplet(monkeypatch):
    monkeypatch.setenv("MEALIE_URL", "https://mealie.test")
    monkeypatch.setenv("MEALIE_API_TOKEN", "token")
    monkeypatch.setenv("OAUTH_ISSUER_URL", "https://auth.test")
    monkeypatch.setenv("OAUTH_CLIENT_ID", "client")
    monkeypatch.delenv("OAUTH_SERVER_URL", raising=False)
    assert server._load_settings()[2] is None
    monkeypatch.setenv("OAUTH_SERVER_URL", "https://mcp.test/mcp")
    monkeypatch.setenv("OAUTH_CLIENT_SECRET", "secret")
    oauth = server._load_settings()[2]
    assert oauth.issuer_url == "https://auth.test"
    assert oauth.client_secret == "secret"
    assert server._oauth_protected_resource_metadata_url(oauth.server_url) == (
        "https://mcp.test/.well-known/oauth-protected-resource/mcp"
    )


def test_server_rejects_unknown_transport_without_starting(monkeypatch):
    monkeypatch.setenv("MEALIE_URL", "https://mealie.test")
    monkeypatch.setenv("MEALIE_API_TOKEN", "token")
    monkeypatch.setenv("MCP_TRANSPORT", "unknown")
    with pytest.raises(RuntimeError, match="Unknown MCP_TRANSPORT"):
        server.run()


def test_transport_allowed_hosts_and_origins_are_trimmed(monkeypatch):
    monkeypatch.setenv("MEALIE_URL", "https://mealie.test")
    monkeypatch.setenv("MEALIE_API_TOKEN", "token")
    monkeypatch.setenv("MCP_ALLOWED_HOSTS", "one.test, ,two.test")
    monkeypatch.setenv("MCP_ALLOWED_ORIGINS", "https://one.test, https://two.test")
    app = server.build_server()
    server._configure_transport_security(app)
    assert "one.test" in app.settings.transport_security.allowed_hosts
    assert "two.test" in app.settings.transport_security.allowed_hosts
    assert "https://two.test" in app.settings.transport_security.allowed_origins
