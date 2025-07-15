"""Main application window placeholder."""

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

    class MainWindow(Gtk.ApplicationWindow):  # pragma: no cover - UI code
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.set_title("Worklog")
            self.set_default_size(800, 600)
            self.set_titlebar(None)

            toolbar = Gtk.HeaderBar()
            toolbar.set_show_close_button(False)
            toolbar.set_title_widget(Gtk.Label(label="Worklog"))

            content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            content.append(toolbar)
            content.append(Gtk.Label(label="Main Window Placeholder"))
            self.set_child(content)
else:

    class MainWindow:  # type: ignore[misc]
        pass
