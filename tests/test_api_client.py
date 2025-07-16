import os
import sys
from types import SimpleNamespace
import types

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Provide a minimal requests stub so the module imports without network deps
requests_stub = types.SimpleNamespace(HTTPError=Exception)
requests_stub.get = lambda *a, **k: None
sys.modules['requests'] = requests_stub

import pytest
from worklog.services import api_client
import requests  # this will be the stub


class DummyResp:
    def __init__(self, status_code: int, data=None):
        self.status_code = status_code
        self._data = data or {}

    def json(self):
        return self._data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} err")


def test_get_worklogs_sends_auth(monkeypatch):
    captured = {}

    def fake_get(url, headers=None, params=None, timeout=10):
        captured['url'] = url
        captured['headers'] = headers
        captured['params'] = params
        return DummyResp(200, {'data': []})

    monkeypatch.setattr(api_client.requests, 'get', fake_get)

    result = api_client.get_worklogs('tok123', page=2)
    assert result == {'data': []}
    assert captured['url'] == 'https://work-log.cc/api/worklogs'
    assert captured['headers']['Authorization'] == 'Bearer tok123'
    assert captured['params']['page'] == 2


def test_get_worklogs_signs_out_on_401(monkeypatch):
    called = {}

    def fake_get(url, headers=None, params=None, timeout=10):
        return DummyResp(401)

    def fake_sign_out():
        called['yes'] = True

    monkeypatch.setattr(api_client.requests, 'get', fake_get)

    with pytest.raises(requests.HTTPError):
        api_client.get_worklogs('bad', sign_out=fake_sign_out)
    assert called.get('yes')
