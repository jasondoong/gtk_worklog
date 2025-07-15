"""Application setup for Worklog."""
from typing import Optional

try:
    import gi
    gi.require_version("Gtk", "4.0")
    gi.require_version("Adw", "1")
    from gi.repository import Adw, Gio, Gtk, GLib
    GTK_AVAILABLE = True
except Exception:  # pragma: no cover - gi not installed
    Adw = Gio = Gtk = GLib = None  # type: ignore
    GTK_AVAILABLE = False


if GTK_AVAILABLE:

    class WorklogApplication(Adw.Application):
        """Main application class following the high-level architecture."""

        def __init__(self):
            super().__init__(application_id="org.worklog")
            self.main_window: Optional[Gtk.Window] = None
            self.connect("startup", self.on_startup)
            self.connect("activate", self.on_activate)

        def on_startup(self, app: Adw.Application) -> None:  # pragma: no cover - UI code
            GLib.set_application_name("Worklog")
            GLib.set_prgname("worklog")

        def on_activate(self, app: Adw.Application) -> None:  # pragma: no cover - UI code
            if self.main_window is None:
                from .ui.main_window import MainWindow
                self.main_window = MainWindow(application=self)
            self.main_window.present()

else:

    class WorklogApplication:  # type: ignore[misc]
        """Dummy fallback application used when Gtk is unavailable."""

        def run(self) -> None:  # pragma: no cover - no GUI
            raise RuntimeError("GTK is not available")
