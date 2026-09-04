from fastapi.testclient import TestClient

from app.hitl import put_in_review
from app.main import app
from app.session import get_state, reset_store
from tests.test_hitl import _tiny_pack


def _client() -> TestClient:
    return TestClient(app)


def _login(client: TestClient, role: str = "product", name: str = "Siddharth"):
    return client.post(
        "/login",
        data={"name": name, "role": role},
        follow_redirects=False,
    )


def test_shared_palette_is_served():
    res = _client().get("/static/maple.css")
    assert res.status_code == 200
    assert "--bg:" in res.text
    assert "--tab:" in res.text


def test_login_page_is_html():
    res = _client().get("/login")
    assert res.status_code == 200
    assert "Dev log in" in res.text
    assert "product" in res.text
    assert "/static/maple.css" in res.text


def test_login_post_sets_cookie_and_redirects():
    res = _login(_client())
    assert res.status_code == 303
    assert res.headers["location"] == "/p/porter"
    assert "maple_token" in res.cookies


def test_workbench_without_cookie_goes_to_login():
    res = _client().get("/p/porter", follow_redirects=False)
    assert res.status_code == 303
    assert res.headers["location"] == "/login"


def test_home_without_cookie_goes_to_login():
    res = _client().get("/", follow_redirects=False)
    assert res.status_code == 303
    assert res.headers["location"] == "/login"


def test_workbench_after_login_shows_role():
    client = _client()
    _login(client)
    res = client.get("/p/porter")
    assert res.status_code == 200
    assert "Siddharth" in res.text
    assert "product" in res.text
    assert "No pack yet" in res.text
    assert "Run Discovery" in res.text
    assert "Sunset" in res.text


def test_logout_clears_cookie():
    client = _client()
    _login(client)
    out = client.get("/logout", follow_redirects=False)
    assert out.status_code == 303
    again = client.get("/p/porter", follow_redirects=False)
    assert again.status_code == 303
    assert again.headers["location"] == "/login"


def test_page_sign_unlocks_stage_2():
    reset_store()
    client = _client()
    _login(client, role="product")
    put_in_review(get_state("page-sign"), _tiny_pack())
    res = client.post("/p/page-sign/sign", follow_redirects=False)
    assert res.status_code == 303
    page = client.get("/p/page-sign")
    assert "signed" in page.text
    assert "[1, 2]" in page.text
    assert 'class="tab on"' in page.text
    assert "Decision" in page.text
    assert "Briefing" in page.text
    assert "Run Strategy" in page.text


def test_page_reject_stays_on_stage_1():
    reset_store()
    client = _client()
    _login(client, role="product")
    put_in_review(get_state("page-reject"), _tiny_pack())
    res = client.post("/p/page-reject/reject", follow_redirects=False)
    assert res.status_code == 303
    page = client.get("/p/page-reject")
    assert "rejected" in page.text
    assert "[1]" in page.text
    assert "[1, 2]" not in page.text


def test_finance_page_sign_shows_error():
    reset_store()
    client = _client()
    _login(client, role="finance")
    put_in_review(get_state("page-finance"), _tiny_pack())
    res = client.post("/p/page-finance/sign", follow_redirects=False)
    assert res.status_code == 303
    assert "cannot%20sign" in res.headers["location"]
    page = client.get(res.headers["location"])
    assert "cannot sign" in page.text
    assert "[1, 2]" not in page.text
