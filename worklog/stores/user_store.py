"""User authentication state store."""

try:
    import gi
    gi.require_version("GObject", "2.0")
    gi.require_version("GLib", "2.0")
    from gi.repository import GObject, GLib
    GI_AVAILABLE = True
except Exception:  # pragma: no cover - gi not installed
    GI_AVAILABLE = False

    class GObject:
        class Object:
            pass

        class Property:  # pragma: no cover - simplified stub
            def __init__(self, **kwargs):
                pass

    class GLib:
        @staticmethod
        def timeout_add_seconds(interval: int, func):
            return None

        @staticmethod
        def source_remove(source):
            pass

import base64
import json
from pathlib import Path
from typing import Dict, Optional
import threading

from ..auth.firebase import load_firebase_config

_ENC_KEY = b"worklog"
_DEFAULT_REFRESH_INTERVAL = 55 * 60  # 55 minutes


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

        def __init__(
            self,
            refresh_interval: int = _DEFAULT_REFRESH_INTERVAL,
            auto_refresh: bool = True,
        ) -> None:
            super().__init__()
            self.token: str | None = None
            self.refresh_token: str | None = None
            self._cred_path = _get_cred_path()
            self._firebase_cfg = load_firebase_config()
            self._refresh_interval = refresh_interval
            self._refresh_source: int | None = None
            self.load_credentials()
            if auto_refresh and self.refresh_token:
                self.refresh_id_token()
                if self.refresh_token and self.token:
                    self._start_refresh_timer()

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

        # ── Refresh helpers ─────────────────────────────────────────
        def _start_refresh_timer(self) -> None:
            if self._refresh_source is None and self.refresh_token:
                self._refresh_source = GLib.timeout_add_seconds(
                    self._refresh_interval,
                    self._on_refresh_timer,
                )

        def _on_refresh_timer(self) -> bool:
            self.refresh_id_token()
            if self.token:
                return True
            self._refresh_source = None
            return False

        def _stop_refresh_timer(self) -> None:
            if self._refresh_source is not None:
                GLib.source_remove(self._refresh_source)
                self._refresh_source = None

        def sign_in(self, id_token: str, refresh_token: str) -> None:
            self.token = id_token
            self.refresh_token = refresh_token
            self.save_credentials()
            self._start_refresh_timer()

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
            url = (
                "https://securetoken.googleapis.com/v1/token?key="
                + self._firebase_cfg["apiKey"]
            )
            req = request.Request(
                url,
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
            self._stop_refresh_timer()
            self.token = None
            self.refresh_token = None
            _clear_credentials(self._cred_path)

else:

    class UserStore:  # type: ignore[misc]
        """Non‑GTK fallback implementation."""

        def __init__(
            self,
            refresh_interval: int = _DEFAULT_REFRESH_INTERVAL,
            auto_refresh: bool = True,
        ):
            self.token: str | None = None
            self.refresh_token: str | None = None
            self._cred_path = _get_cred_path()
            self._firebase_cfg = load_firebase_config()
            self._refresh_interval = refresh_interval
            self._refresh_thread: threading.Timer | None = None
            self.load_credentials()
            if auto_refresh and self.refresh_token:
                self.refresh_id_token()
                if self.refresh_token and self.token:
                    self._start_refresh_timer()

        def load_credentials(self) -> None:  # pragma: no cover - placeholder
            creds = _load_encrypted(self._cred_path)
            if creds:
                self.token = creds.get("id_token")
                self.refresh_token = creds.get("refresh_token")

        def save_credentials(self) -> None:
            if self.token and self.refresh_token:
                data = {"id_token": self.token, "refresh_token": self.refresh_token}
                _save_encrypted(self._cred_path, data)

        def _start_refresh_timer(self) -> None:
            if self._refresh_thread is None and self.refresh_token:
                self._refresh_thread = threading.Timer(
                    self._refresh_interval,
                    self._refresh_timer,
                )
                self._refresh_thread.daemon = True
                self._refresh_thread.start()

        def _refresh_timer(self) -> None:
            self.refresh_id_token()
            if self.token:
                self._refresh_thread = threading.Timer(
                    self._refresh_interval,
                    self._refresh_timer,
                )
                self._refresh_thread.daemon = True
                self._refresh_thread.start()
            else:
                self._refresh_thread = None

        def _stop_refresh_timer(self) -> None:
            if self._refresh_thread is not None:
                self._refresh_thread.cancel()
                self._refresh_thread = None

        def sign_in(self, id_token: str, refresh_token: str) -> None:
            self.token = id_token
            self.refresh_token = refresh_token
            self.save_credentials()
            self._start_refresh_timer()

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
            url = (
                "https://securetoken.googleapis.com/v1/token?key="
                + self._firebase_cfg["apiKey"]
            )
            req = request.Request(
                url,
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
            self._stop_refresh_timer()
            self.token = None
            self.refresh_token = None
            _clear_credentials(self._cred_path)
