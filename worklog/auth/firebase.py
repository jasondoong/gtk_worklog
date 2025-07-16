import json
import os
from pathlib import Path
from typing import Dict


_CONFIG_PATH = Path.home() / ".config" / "worklog" / "firebase_config.json"
_GOOGLE_OAUTH_PATH = Path.home() / ".config" / "worklog" / "google_oauth_client.json"


def load_firebase_config() -> Dict[str, str]:
    """Load Firebase project configuration.

    The configuration is read from ``~/.config/worklog/firebase_config.json`` if
    present. Otherwise environment variables prefixed with ``WORKLOG_FB_`` are
    used. At minimum, ``apiKey`` must be provided.  Raises ``RuntimeError`` if
    the configuration cannot be found.
    """
    if _CONFIG_PATH.exists():
        try:
            with _CONFIG_PATH.open("r", encoding="utf-8") as fh:
                cfg = json.load(fh)
            if "apiKey" in cfg:
                return cfg
        except Exception:
            pass
    # Fallback to environment variables
    api_key = os.getenv("WORKLOG_FB_API_KEY")
    if api_key:
        cfg = {"apiKey": api_key}
        client_id = os.getenv("WORKLOG_FB_CLIENT_ID")
        project_id = os.getenv("WORKLOG_FB_PROJECT_ID")
        if client_id:
            cfg["clientId"] = client_id
        if project_id:
            cfg["projectId"] = project_id
        return cfg

    raise RuntimeError("Firebase configuration missing")


def load_google_oauth_client() -> Dict[str, str]:
    """Load Google OAuth client configuration for the desktop app.

    Looks for ``~/.config/worklog/google_oauth_client.json`` which should be the
    "installed" JSON downloaded from Google Cloud. If the file is absent,
    ``WORKLOG_GOOGLE_CLIENT_ID`` environment variable is used.  At minimum,
    ``client_id`` must be provided.
    """
    if _GOOGLE_OAUTH_PATH.exists():
        try:
            with _GOOGLE_OAUTH_PATH.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
            if "installed" in data:
                data = data["installed"]
            if "client_id" in data:
                return data
        except Exception:
            pass
    client_id = os.getenv("WORKLOG_GOOGLE_CLIENT_ID")
    if client_id:
        return {"client_id": client_id}
    raise RuntimeError("Google OAuth client configuration missing")
