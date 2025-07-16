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
        """Simple login window with Google sign in only."""

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
            google_btn.connect("clicked", self.on_google)

            btn_box = Gtk.Box(spacing=12)
            btn_box.append(google_btn)

            box.append(btn_box)

            self.set_content(box)

        def on_google(self, _button: Gtk.Button) -> None:
            import webbrowser
            webbrowser.open("https://accounts.google.com/o/oauth2/v2/auth")
else:

    class LoginWindow:  # type: ignore[misc]
        pass
