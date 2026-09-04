import io
import shutil
import zipfile
from pathlib import Path

from fastapi.testclient import TestClient

from app.ingest import bytes_to_markdown, ingest, unpack_zip, resolve_product
from app.main import app
from app.rag.admit import admitted_paths, inputs_root, repo_root
from tests.test_pages_login import _login


def test_onboard_requires_login():
    res = TestClient(app).get("/onboard", follow_redirects=False)
    assert res.status_code == 303
    assert res.headers["location"] == "/"


def test_onboard_page_has_save_and_logout():
    client = TestClient(app)
    _login(client)
    page = client.get("/onboard")
    assert page.status_code == 200
    assert "Save" in page.text
    assert "Log out" in page.text
    assert "Onboard research" in page.text
    assert "Discovery" in page.text
    assert "Existing product" in page.text
    assert "New product name" in page.text


def test_onboard_kit_is_zip():
    res = TestClient(app).get("/onboard/kit.zip")
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("application/zip")
    zf = zipfile.ZipFile(io.BytesIO(res.content))
    names = zf.namelist()
    assert "s1_discovery/README.md" in names
    assert "s9_sunset/README.md" in names


def test_txt_and_png_ingest_to_product_folder():
    slug = "pytest-acme"
    dest = repo_root() / "data" / "products" / slug
    if dest.exists():
        shutil.rmtree(dest)
    try:
        report = ingest(
            "Pytest Acme",
            "Acme",
            1,
            [
                ("voc.txt", b"Priya misses the shutoff notice."),
                ("photo.png", b"\x89PNG\r\nnot-a-real-image"),
            ],
        )
        assert report["slug"] == slug
        assert report["extracted"] == 1
        assert report["stubs"] == 1
        assert report["rooms"]["s1_discovery"] == 2
        root = inputs_root(slug)
        assert "products" in root.as_posix()
        paths = [p.name for p in admitted_paths([1], slug)]
        assert "voc.md" in paths
        joined = "\n".join(p.as_posix() for p in admitted_paths([1], slug))
        assert "s9_sunset" not in joined
        assert "raw_inputs" not in joined
        porter = "\n".join(p.as_posix() for p in admitted_paths([1], "porter"))
        assert "raw_inputs" in porter
    finally:
        if dest.exists():
            shutil.rmtree(dest)


def test_second_dump_adds_to_existing_product():
    slug = "pytest-keep"
    dest = repo_root() / "data" / "products" / slug
    if dest.exists():
        shutil.rmtree(dest)
    try:
        ingest("Pytest Keep", "", 1, [("first.txt", b"alpha")])
        ingest("Pytest Keep", "", 1, [("second.txt", b"beta")])
        names = [p.name for p in admitted_paths([1], slug)]
        assert "first.md" in names
        assert "second.md" in names
        assert resolve_product("ignored", "pytest-keep") == "pytest-keep"
    finally:
        if dest.exists():
            shutil.rmtree(dest)


def test_zip_folder_names_beat_dropdown():
    slug = "pytest-zip"
    dest = repo_root() / "data" / "products" / slug
    if dest.exists():
        shutil.rmtree(dest)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("s2_strategy/pricing.txt", "per door napkin")
    try:
        report = ingest("Pytest Zip", "", 1, [("dump.zip", buf.getvalue())])
        assert report["rooms"]["s2_strategy"] == 1
        assert report["rooms"]["s1_discovery"] == 0
    finally:
        if dest.exists():
            shutil.rmtree(dest)


def test_zip_path_traversal_rejected():
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("../evil.md", "nope")
    try:
        unpack_zip(buf.getvalue())
        raise AssertionError("should have rejected")
    except ValueError as exc:
        assert "unsafe" in str(exc)


def test_png_is_stub_not_dropped():
    text, how = bytes_to_markdown("shot.png", b"nope")
    assert how == "stub"
    assert "shot.png" in text


def test_onboard_post_saves_and_shows_receipt():
    slug = "pytest-web"
    dest = repo_root() / "data" / "products" / slug
    if dest.exists():
        shutil.rmtree(dest)
    client = TestClient(app)
    _login(client)
    try:
        res = client.post(
            "/onboard",
            data={"product": "Pytest Web", "company": "Co", "room": "unsure"},
            files=[("files", ("notes.txt", b"jobs to be done", "text/plain"))],
        )
        assert res.status_code == 200
        assert "Saved." in res.text
        assert "Log out" in res.text
        assert "jobs to be done" in Path(
            dest / "s1_discovery" / "notes.md"
        ).read_text(encoding="utf-8")
    finally:
        if dest.exists():
            shutil.rmtree(dest)


def test_porter_name_rejected():
    try:
        ingest("porter", "", 1, [("a.txt", b"x")])
        raise AssertionError("should have rejected")
    except ValueError as exc:
        assert "sample" in str(exc).lower()
