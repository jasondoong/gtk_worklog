"""Login window placeholder."""

try:
    import gi
    gi.require_version("Gtk", "4.0")
    gi.require_version("Adw", "1")
    from gi.repository import Adw, Gtk
    GTK_AVAILABLE = True
except Exception:  # pragma: no cover - gi not installed
    Adw = Gtk = None  # type: ignore
    GTK_AVAILABLE = False

if GTK_AVAILABLE:

    class LoginWindow(Adw.ApplicationWindow):  # pragma: no cover - UI code
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.set_title("Worklog • Sign in")
            self.set_default_size(400, 200)
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12, margin_top=20)
            box.append(Gtk.Label(label="Login Placeholder"))
            self.set_content(box)
else:

    class LoginWindow:  # type: ignore[misc]
        pass
