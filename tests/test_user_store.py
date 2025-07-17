import os
import sys
import types

# Ensure project root on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from worklog.stores import user_store
from worklog.stores.user_store import UserStore


def test_user_store_token_default():
    os.environ["WORKLOG_FB_API_KEY"] = "testkey"
    store = UserStore(auto_refresh=False)
    assert getattr(store, "token", None) is None


def test_sign_in_persists_credentials(monkeypatch, tmp_path):
    monkeypatch.setattr(user_store.Path, "home", lambda: tmp_path)
    monkeypatch.setenv("WORKLOG_FB_API_KEY", "testkey")
    store = UserStore(auto_refresh=False)
    store.sign_in("id1", "refresh1")
    assert store.token == "id1"
    path = store._cred_path
    assert path.exists()

    # Reload to ensure persistence
    store2 = UserStore(auto_refresh=False)
    assert store2.token == "id1"
    assert store2.refresh_token == "refresh1"

    store2.sign_out()
    assert not path.exists()


def test_refresh_adds_api_key(monkeypatch, tmp_path):
    monkeypatch.setattr(user_store.Path, "home", lambda: tmp_path)
    monkeypatch.setenv("WORKLOG_FB_API_KEY", "dummy")
    store = UserStore(auto_refresh=False)
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


def test_sign_in_starts_timer(monkeypatch):
    monkeypatch.setenv("WORKLOG_FB_API_KEY", "dummy")
    events = {}

    class DummyTimer:
        def __init__(self, interval, func):
            events['interval'] = interval
            self.func = func

        def start(self):
            events['started'] = True

        def cancel(self):
            events['canceled'] = True

    monkeypatch.setattr(user_store, "threading", types.SimpleNamespace(Timer=DummyTimer))
    store = UserStore(refresh_interval=1)
    store.sign_in("t", "r")
    assert events.get('started')
    assert events['interval'] == 1
    store.sign_out()
    assert events.get('canceled')


def test_refresh_on_init(monkeypatch, tmp_path):
    monkeypatch.setattr(user_store.Path, "home", lambda: tmp_path)
    monkeypatch.setenv("WORKLOG_FB_API_KEY", "dummy")
    store = UserStore(auto_refresh=False)
    store.sign_in("tid", "rtoken")

    called = {}

    class DummyTimer:
        def __init__(self, interval, func):
            called['interval'] = interval
            self.func = func

        def start(self):
            called['started'] = True

        def cancel(self):
            called['canceled'] = True

    monkeypatch.setattr(user_store, "threading", types.SimpleNamespace(Timer=DummyTimer))

    def fake_refresh(self):
        called['refreshed'] = True

    monkeypatch.setattr(UserStore, "refresh_id_token", fake_refresh)
    store2 = UserStore(refresh_interval=1)
    assert called.get('refreshed')
    assert called.get('started')

