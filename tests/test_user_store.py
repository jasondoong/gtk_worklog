import os
import sys

# Ensure project root on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from worklog.stores.user_store import UserStore


def test_user_store_token_default():
    store = UserStore()
    assert getattr(store, "token", None) is None
