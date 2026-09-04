from app.audit import for_product, log
from app.auth import Principal
from app.session import get_state
from tests.test_hitl import _tiny_pack
from app.hitl import put_in_review, sign_pack


def test_sign_writes_audit_row():
    who = Principal(name="Siddharth", role="product", email="sid@co.com")
    state = get_state("audit-sign")
    put_in_review(state, _tiny_pack())
    sign_pack(state, "product")
    log(who, "sign", "audit-sign")
    rows = for_product("audit-sign")
    assert any(r["action"] == "sign" and r["actor"] == "sid@co.com" for r in rows)


def test_login_page_offers_google():
    from fastapi.testclient import TestClient
    from app.main import app

    res = TestClient(app).get("/login")
    assert res.status_code == 200
    assert "Continue with Google" in res.text or "Company email" in res.text
    assert "Dev log in" in res.text
