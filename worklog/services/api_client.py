"""HTTP API client helpers for worklog backend."""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

import requests

API_BASE = "https://work-log.cc/api"


def _handle_auth(resp: requests.Response, sign_out: Optional[Callable[[], None]] = None) -> None:
    """Trigger sign out if response indicates authentication failure."""
    if resp.status_code in (401, 403):
        if sign_out:
            sign_out()


def get_worklogs(token: str, *, sign_out: Optional[Callable[[], None]] = None, **params: Any) -> Dict[str, Any]:
    """Return worklogs JSON from the backend.

    Parameters
    ----------
    token:
        ID token for the current user.
    sign_out:
        Optional callback invoked when the server responds with 401 or 403.
    params:
        Query parameters forwarded to the API.
    """
    url = f"{API_BASE}/worklogs"
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(url, headers=headers, params=params, timeout=10)
    _handle_auth(resp, sign_out)
    resp.raise_for_status()
    return resp.json()
