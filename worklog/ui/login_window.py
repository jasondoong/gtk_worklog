"""Login window implementation following the specification."""

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
        """Simple login window with two sign in options."""

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

            self.set_title("Worklog • Sign in")
            self.set_default_size(400, 200)

            # Header bar
            header = Gtk.HeaderBar()
            header.set_show_close_button(True)
            title_label = Gtk.Label(label="Worklog • Sign in")
            header.set_title_widget(title_label)
            self.set_titlebar(header)

            # Content area
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12, margin_top=20)
            box.set_halign(Gtk.Align.CENTER)
            box.set_valign(Gtk.Align.CENTER)

            google_btn = Gtk.Button(label="Google")
            email_btn = Gtk.Button(label="Email & password")

            btn_box = Gtk.Box(spacing=12)
            btn_box.append(google_btn)
            btn_box.append(email_btn)

            box.append(btn_box)

            self.set_content(box)
else:

    class LoginWindow:  # type: ignore[misc]
        pass
