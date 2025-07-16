try:
    import gi
    gi.require_version("Gtk", "4.0")
    gi.require_version("Gio", "2.0")
    gi.require_version("GObject", "2.0")
    from gi.repository import Gtk, Gio, GObject
    GTK_AVAILABLE = True
except Exception:  # pragma: no cover - gi not installed
    Gtk = Gio = GObject = None  # type: ignore
    GTK_AVAILABLE = False

from ..stores.user_store import UserStore
from .login_window import LoginWindow
from .log_item import DateHeader, LogItem

if GTK_AVAILABLE:

    class MainWindow(Gtk.ApplicationWindow):  # pragma: no cover – UI code
        """Primary application window with basic layout widgets."""

        def __init__(self, user_store: UserStore, **kwargs):
            super().__init__(**kwargs)
            self.user_store = user_store

            self.set_title("Worklog")
            self.set_default_size(800, 600)

            header = Gtk.HeaderBar()
            header.set_show_title_buttons(True)

            title_label = Gtk.Label(label="Worklog")
            header.set_title_widget(title_label)

            space_btn = Gtk.Button(label="default")
            space_btn.set_focusable(False)
            space_btn.set_valign(Gtk.Align.CENTER)

            prev_btn = Gtk.Button()
            prev_btn.set_child(Gtk.Image.new_from_icon_name("go-previous-symbolic"))
            next_btn = Gtk.Button()
            next_btn.set_child(Gtk.Image.new_from_icon_name("go-next-symbolic"))
            month_lbl = Gtk.Label(label="Month July 2025")
            nav_box = Gtk.Box(spacing=6)
            nav_box.append(prev_btn)
            nav_box.append(month_lbl)
            nav_box.append(next_btn)

            search_entry = Gtk.SearchEntry()
            menu_btn = Gtk.Button()
            menu_btn.set_child(Gtk.Image.new_from_icon_name("open-menu-symbolic"))
            menu_btn.connect("clicked", self.on_logout)

            header.pack_start(space_btn)
            header.pack_end(menu_btn)
            header.pack_end(search_entry)
            header.pack_end(nav_box)

            self.set_titlebar(header)

            self._list_store = Gio.ListStore.new(GObject.Object)
            self._selection = Gtk.NoSelection.new(self._list_store)

            factory = Gtk.SignalListItemFactory()
            factory.connect("setup", self._on_item_setup)
            factory.connect("bind", self._on_item_bind)

            self.list_view = Gtk.ListView.new(self._selection, factory)

            scrolled = Gtk.ScrolledWindow()
            scrolled.set_child(self.list_view)
            self.set_child(scrolled)

            self.refresh()

        def on_logout(self, _button: Gtk.Button) -> None:
            self.user_store.sign_out()
            win = LoginWindow(application=self.get_application())
            win.present()
            self.close()

        # ── ListView helpers ──────────────────────────────────────────
        def _on_item_setup(self, _factory: Gtk.ListItemFactory, item: Gtk.ListItem) -> None:
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            time_label = Gtk.Label(xalign=0)
            content_label = Gtk.Label(xalign=0)
            box.append(time_label)
            box.append(content_label)
            item.set_child(box)
            item.time_label = time_label  # type: ignore[attr-defined]
            item.content_label = content_label  # type: ignore[attr-defined]

        def _on_item_bind(self, _factory: Gtk.ListItemFactory, item: Gtk.ListItem) -> None:
            data = item.get_item()
            time_label = item.time_label  # type: ignore[attr-defined]
            content_label = item.content_label  # type: ignore[attr-defined]
            if isinstance(data, DateHeader):
                time_label.set_markup(f"<b>{data.date}</b>")
                content_label.set_text("")
            elif isinstance(data, LogItem):
                time_label.set_text(data.time)
                content_label.set_text(data.text)
            else:
                time_label.set_text("")
                content_label.set_text("")

        # ── Data loading ──────────────────────────────────────────────
        def refresh(self) -> None:
            token = self.user_store.token
            if not token:
                return
            from ..services import api_client

            try:
                payload = api_client.get_worklogs(token, sign_out=self._handle_sign_out)
            except Exception:
                return

            logs = payload.get("data", [])
            items: list[GObject.Object] = []
            current_date = None
            for log in logs:
                dt = str(log.get("record_time", ""))[:10]
                if dt != current_date:
                    current_date = dt
                    items.append(DateHeader(current_date))
                time_str = str(log.get("record_time", ""))[11:16]
                text = log.get("content", "")
                items.append(LogItem(time_str, text))

            self._list_store.remove_all()
            for item in items:
                self._list_store.append(item)

        def _handle_sign_out(self) -> None:
            self.user_store.sign_out()
            win = LoginWindow(application=self.get_application())
            win.present()
            self.close()

else:

    class MainWindow:  # type: ignore[misc]
        pass
