import os
import sys

# Ensure project root on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from worklog.stores import user_store
from worklog.stores.user_store import UserStore


def test_user_store_token_default():
    os.environ["WORKLOG_FB_API_KEY"] = "testkey"
    store = UserStore()
    assert getattr(store, "token", None) is None


def test_sign_in_persists_credentials(monkeypatch, tmp_path):
    monkeypatch.setattr(user_store.Path, "home", lambda: tmp_path)
    monkeypatch.setenv("WORKLOG_FB_API_KEY", "testkey")
    store = UserStore()
    store.sign_in("id1", "refresh1")
    assert store.token == "id1"
    path = store._cred_path
    assert path.exists()

    # Reload to ensure persistence
    store2 = UserStore()
    assert store2.token == "id1"
    assert store2.refresh_token == "refresh1"

    store2.sign_out()
    assert not path.exists()


def test_refresh_adds_api_key(monkeypatch, tmp_path):
    monkeypatch.setattr(user_store.Path, "home", lambda: tmp_path)
    monkeypatch.setenv("WORKLOG_FB_API_KEY", "dummy")
    store = UserStore()
    store.refresh_token = "r1"

    captured = {}

    class DummyResp:
        def read(self):
            return b'{"id_token": "tid"}'

    def fake_urlopen(req, timeout=10):
        captured['url'] = req.full_url
        return DummyResp()

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)
    store.refresh_id_token()
    assert captured['url'].endswith("?key=dummy")
