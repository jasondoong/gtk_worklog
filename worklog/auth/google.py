"""Google OAuth helper functions for the Worklog desktop app.

This module runs the InstalledApp (loopback) OAuth flow in the user's default
browser and returns the Google ID token. It then provides a helper to exchange
that ID token for Firebase credentials (idToken + refreshToken) via the
Identity Toolkit `accounts:signInWithIdp` REST endpoint.

Usage:
    from worklog.auth.google import do_google_oauth, exchange_google_to_firebase

    google_id_token, _google_refresh = do_google_oauth()
    fb_id_token, fb_refresh_token = exchange_google_to_firebase(api_key, google_id_token)

Configuration:
    Expects the Google *Desktop app* client secret JSON at:
        ~/.config/worklog/google_oauth_client.json
    This is the JSON you download from Google Cloud Console when you create an
    OAuth Client ID of type "Desktop app".

    Your Firebase Web API Key is loaded separately (see worklog/auth/firebase.py).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Tuple

import requests

# Scopes required to receive an ID token that includes the user's identity.
# Use the canonical userinfo scope URIs to avoid scope mismatch warnings.
SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]

# Location where the user should drop the downloaded *Desktop app* client JSON.
_GOOGLE_OAUTH_PATH = Path.home() / ".config" / "worklog" / "google_oauth_client.json"


def _client_secrets_path() -> Path:
    """Return the path to the client_secret JSON; raise if missing."""
    if _GOOGLE_OAUTH_PATH.exists():
        return _GOOGLE_OAUTH_PATH
    raise RuntimeError(
        f"Google OAuth client secrets not found at {_GOOGLE_OAUTH_PATH}.\n"
        "Download the *Desktop app* (Installed) client JSON from Google Cloud "
        "and save it there."
    )


def do_google_oauth() -> Tuple[str, str | None]:
    """Run the InstalledAppFlow and return (google_id_token, google_refresh_token?)."""
    from google_auth_oauthlib.flow import InstalledAppFlow  # import locally to avoid heavy import cost
    from google.auth.transport.requests import Request as GARequest

    secrets = _client_secrets_path()
    flow = InstalledAppFlow.from_client_secrets_file(str(secrets), SCOPES)
    # Opens the system browser and spins up a local HTTP server on a free port (port=0).
    creds = flow.run_local_server(port=0, open_browser=True)

    # creds.id_token normally populated when "openid" scope requested.
    google_id_token = getattr(creds, "id_token", None)
    if not google_id_token:
        # Force refresh to try populating id_token (defensive).
        try:  # pragma: no cover - defensive path
            creds.refresh(GARequest())
            google_id_token = getattr(creds, "id_token", None)
        except Exception as exc:  # pragma: no cover - defensive path
            raise RuntimeError(f"Google OAuth succeeded but no ID token available: {exc}") from exc

    if not google_id_token:
        raise RuntimeError("Google OAuth succeeded but ID token missing.")

    google_refresh_token = getattr(creds, "refresh_token", None)
    return google_id_token, google_refresh_token


def exchange_google_to_firebase(api_key: str, google_id_token: str) -> Tuple[str, str]:
    """Exchange a Google ID token for Firebase ID/refresh tokens.

    Args:
        api_key: Firebase Web API Key (Project settings > General > Web API Key).
        google_id_token: ID token from Google OAuth (do_google_oauth()).

    Returns:
        (firebase_id_token, firebase_refresh_token)
    """
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp?key={api_key}"
    payload = {
        # For manual credential exchange, Google docs allow http://localhost.
        "requestUri": "http://localhost",
        "postBody": f"id_token={google_id_token}&providerId=google.com",
        "returnSecureToken": True,
    }
    resp = requests.post(url, json=payload, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    try:
        fb_id_token = data["idToken"]
        fb_refresh_token = data["refreshToken"]
    except KeyError as exc:  # pragma: no cover - defensive
        raise RuntimeError(
            f"Firebase exchange response missing field: {exc}; payload={json.dumps(data)[:200]}"
        ) from exc

    return fb_id_token, fb_refresh_token

