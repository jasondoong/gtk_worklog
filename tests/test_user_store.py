import os
import sys

# Ensure project root on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from worklog.stores import user_store
from worklog.stores.user_store import UserStore


def test_user_store_token_default():
    store = UserStore()
    assert getattr(store, "token", None) is None


def test_sign_in_persists_credentials(monkeypatch, tmp_path):
    monkeypatch.setattr(user_store.Path, "home", lambda: tmp_path)
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
