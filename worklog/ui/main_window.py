"""Main application window implementation following the specification."""

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
        """Primary application window with basic layout widgets."""

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

            self.set_title("Worklog")
            self.set_default_size(800, 600)

            # Header bar with simple toolbar
            header = Gtk.HeaderBar()
            header.set_show_close_button(True)
            title_label = Gtk.Label(label="Worklog")
            header.set_title_widget(title_label)
            menu_btn = Gtk.Button.new_from_icon_name("open-menu-symbolic")
            search_entry = Gtk.SearchEntry()
            refresh_btn = Gtk.Button.new_from_icon_name("view-refresh-symbolic")
            header.pack_start(menu_btn)
            header.pack_end(refresh_btn)
            header.pack_end(search_entry)
            self.set_titlebar(header)

            # Content: spaces list on the left, logs on the right
            paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)

            spaces_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            spaces_list = Gtk.ListBox()
            spaces_list.append(Gtk.Label(label="My space"))
            spaces_list.append(Gtk.Label(label="Project A"))
            spaces_list.append(Gtk.Label(label="Project B"))
            spaces_box.append(spaces_list)

            logs_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            logs_box.append(Gtk.Label(label="Logs list placeholder"))

            paned.set_start_child(spaces_box)
            paned.set_end_child(logs_box)

            self.set_child(paned)
else:

    class MainWindow:  # type: ignore[misc]
        pass
