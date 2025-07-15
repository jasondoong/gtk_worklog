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


if GI_AVAILABLE:

    class UserStore(GObject.Object):  # pragma: no cover - Gtk specific
        token = GObject.Property(type=str, default=None)

        def load_credentials(self) -> None:
            """Load credentials from configuration."""
            pass
else:

    class UserStore:  # type: ignore[misc]
        def __init__(self):
            self.token = None

        def load_credentials(self) -> None:  # pragma: no cover - placeholder
            pass
