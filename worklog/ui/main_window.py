import gi
gi.require_version("Gtk", "4.0")          # ensure you really use GTK 4
from gi.repository import Gtk

from ..stores.user_store import UserStore
from .login_window import LoginWindow

class MainWindow(Gtk.ApplicationWindow):  # pragma: no cover – UI code
    """Primary application window with basic layout widgets."""

    def __init__(self, user_store: UserStore, **kwargs):
        super().__init__(**kwargs)
        self.user_store = user_store

        self.set_title("Worklog")
        self.set_default_size(800, 600)

        # ── Header bar ───────────────────────────────────────────────
        header = Gtk.HeaderBar()
        header.set_show_title_buttons(True)          # ← GTK 4 API
        title_label = Gtk.Label(label="Worklog")
        header.set_title_widget(title_label)

        menu_btn    = Gtk.Button.new_from_icon_name("open-menu-symbolic")
        search_entry = Gtk.SearchEntry()
        refresh_btn = Gtk.Button.new_from_icon_name("view-refresh-symbolic")
        logout_btn  = Gtk.Button.new_from_icon_name("system-log-out-symbolic")
        logout_btn.connect("clicked", self.on_logout)

        header.pack_start(menu_btn)
        header.pack_end(refresh_btn)
        header.pack_end(logout_btn)
        header.pack_end(search_entry)

        self.set_titlebar(header)

    def on_logout(self, _button: Gtk.Button) -> None:
        self.user_store.sign_out()
        win = LoginWindow(application=self.get_application())
        win.present()
        self.close()

