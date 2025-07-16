"""User authentication state store."""

try:
    import gi
    gi.require_version("GObject", "2.0")
    from gi.repository import GObject
    GI_AVAILABLE = True
except Exception:  # pragma: no cover - gi not installed
    GI_AVAILABLE = False

    class GObject:
        class Object:
            pass

        class Property:  # pragma: no cover - simplified stub
            def __init__(self, **kwargs):
                pass

import base64
import json
from pathlib import Path
from typing import Dict, Optional

_ENC_KEY = b"worklog"


def _get_cred_path() -> Path:
    return Path.home() / ".config" / "worklog" / "credentials.json.enc"


def _encrypt(data: bytes) -> bytes:
    return bytes(b ^ _ENC_KEY[i % len(_ENC_KEY)] for i, b in enumerate(data))


def _save_encrypted(path: Path, data: Dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(data).encode("utf-8")
    enc = base64.b64encode(_encrypt(raw))
    path.write_bytes(enc)


def _load_encrypted(path: Path) -> Optional[Dict[str, str]]:
    if not path.exists():
        return None
    try:
        raw = base64.b64decode(path.read_bytes())
        dec = _encrypt(raw)
        return json.loads(dec.decode("utf-8"))
    except Exception:
        return None


def _clear_credentials(path: Path) -> None:
    if path.exists():
        path.unlink()


if GI_AVAILABLE:

    class UserStore(GObject.Object):  # pragma: no cover - Gtk specific
        """Store and refresh authentication tokens."""

        token = GObject.Property(type=str, default=None)

        def __init__(self) -> None:
            super().__init__()
            self.token: str | None = None
            self.refresh_token: str | None = None
            self._cred_path = _get_cred_path()
            self.load_credentials()

        # ── Public API ────────────────────────────────────────────────
        def load_credentials(self) -> None:
            """Load credentials from disk if present."""
            creds = _load_encrypted(self._cred_path)
            if creds:
                self.token = creds.get("id_token")
                self.refresh_token = creds.get("refresh_token")

        def save_credentials(self) -> None:
            """Persist current tokens."""
            if self.token and self.refresh_token:
                data = {"id_token": self.token, "refresh_token": self.refresh_token}
                _save_encrypted(self._cred_path, data)

        def sign_in(self, id_token: str, refresh_token: str) -> None:
            self.token = id_token
            self.refresh_token = refresh_token
            self.save_credentials()

        def refresh_id_token(self) -> None:
            """Refresh the ID token using the stored refresh token."""
            if not self.refresh_token:
                return
            import json as _json
            from urllib import request, parse

            data = parse.urlencode(
                {
                    "grant_type": "refresh_token",
                    "refresh_token": self.refresh_token,
                }
            ).encode()
            req = request.Request(
                "https://securetoken.googleapis.com/v1/token",
                data=data,
                method="POST",
            )
            try:
                with request.urlopen(req, timeout=10) as resp:
                    payload = _json.loads(resp.read().decode())
                self.token = payload.get("id_token")
                self.save_credentials()
            except Exception:
                self.sign_out()

        def sign_out(self) -> None:
            self.token = None
            self.refresh_token = None
            _clear_credentials(self._cred_path)

else:

    class UserStore:  # type: ignore[misc]
        """Non‑GTK fallback implementation."""

        def __init__(self):
            self.token: str | None = None
            self.refresh_token: str | None = None
            self._cred_path = _get_cred_path()
            self.load_credentials()

        def load_credentials(self) -> None:  # pragma: no cover - placeholder
            creds = _load_encrypted(self._cred_path)
            if creds:
                self.token = creds.get("id_token")
                self.refresh_token = creds.get("refresh_token")

        def save_credentials(self) -> None:
            if self.token and self.refresh_token:
                data = {"id_token": self.token, "refresh_token": self.refresh_token}
                _save_encrypted(self._cred_path, data)

        def sign_in(self, id_token: str, refresh_token: str) -> None:
            self.token = id_token
            self.refresh_token = refresh_token
            self.save_credentials()

        def refresh_id_token(self) -> None:
            if not self.refresh_token:
                return
            import json as _json
            from urllib import request, parse

            data = parse.urlencode(
                {
                    "grant_type": "refresh_token",
                    "refresh_token": self.refresh_token,
                }
            ).encode()
            req = request.Request(
                "https://securetoken.googleapis.com/v1/token",
                data=data,
                method="POST",
            )
            try:
                with request.urlopen(req, timeout=10) as resp:
                    payload = _json.loads(resp.read().decode())
                self.token = payload.get("id_token")
                self.save_credentials()
            except Exception:
                self.sign_out()

        def sign_out(self) -> None:
            self.token = None
            self.refresh_token = None
            _clear_credentials(self._cred_path)
