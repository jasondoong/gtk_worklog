import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from worklog.auth import firebase


def test_load_google_oauth_from_file(tmp_path, monkeypatch):
    d = tmp_path / ".config" / "worklog"
    d.mkdir(parents=True)
    content = {"installed": {"client_id": "abc", "redirect_uris": ["http://localhost"]}}
    path = d / "google_oauth_client.json"
    path.write_text(json.dumps(content))
    monkeypatch.setattr(firebase, "_GOOGLE_OAUTH_PATH", path)
    cfg = firebase.load_google_oauth_client()
    assert cfg["client_id"] == "abc"


def test_load_google_oauth_from_env(tmp_path, monkeypatch):
    monkeypatch.delenv("WORKLOG_GOOGLE_CLIENT_ID", raising=False)
    monkeypatch.setenv("WORKLOG_GOOGLE_CLIENT_ID", "xyz")
    monkeypatch.setattr(firebase, "_GOOGLE_OAUTH_PATH", tmp_path / "doesntexist.json")
    cfg = firebase.load_google_oauth_client()
    assert cfg["client_id"] == "xyz"
