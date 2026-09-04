from app.sso import domain_ok, role_for_email, sso_ready


def test_sso_off_without_google_keys(monkeypatch):
    monkeypatch.setattr("app.sso.settings.google_client_id", "")
    monkeypatch.setattr("app.sso.settings.google_client_secret", "")
    assert sso_ready() is False


def test_role_map_and_default(monkeypatch):
    monkeypatch.setattr(
        "app.sso.settings.sso_role_map",
        "pat@co.com=finance,dev@co.com=engineering",
    )
    monkeypatch.setattr("app.sso.settings.sso_default_role", "product")
    assert role_for_email("pat@co.com") == "finance"
    assert role_for_email("other@co.com") == "product"


def test_domain_gate(monkeypatch):
    monkeypatch.setattr("app.sso.settings.sso_allowed_domain", "co.com")
    assert domain_ok("a@co.com") is True
    assert domain_ok("a@other.com") is False
