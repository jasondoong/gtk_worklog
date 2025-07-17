from __future__ import annotations

"""Primary application window showing worklogs as *date cards* in a grid."""

import datetime as _dt
from collections import defaultdict
from typing import Any, Iterable, Mapping

try:
    import gi  # type: ignore
    gi.require_version("Gtk", "4.0")
    gi.require_version("Gio", "2.0")
    gi.require_version("GObject", "2.0")
    from gi.repository import Gtk, Gio, GObject
    try:
        gi.require_version("Adw", "1")
        from gi.repository import Adw  # noqa: F401
        _ADW = True
    except Exception:
        _ADW = False
    GTK_AVAILABLE = True
except Exception:  # pragma: no cover
    Gtk = Gio = GObject = None  # type: ignore
    _ADW = False
    GTK_AVAILABLE = False

# NOTE: To avoid fragile imports across package refactors we do *lazy* imports
# of LoginWindow and DayCard inside the methods that need them.  This makes the
# module more resilient when used in unit tests with partial stubs.


def _load_css(display: "Gtk.Display") -> None:
    # Load our local CSS if present.
    try:
        from pathlib import Path
        css_path = Path(__file__).with_name("style.css")
        if not css_path.is_file():
            return
        provider = Gtk.CssProvider()
        provider.load_from_path(str(css_path))
        Gtk.StyleContext.add_provider_for_display(
            display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
    except Exception:
        pass


if GTK_AVAILABLE:

    class MainWindow(Gtk.ApplicationWindow):  # pragma: no cover - UI glue
        def __init__(self, user_store: Any, **kwargs):
            super().__init__(**kwargs)
            self.user_store = user_store

            self.set_title("Worklog")
            self.set_default_size(1024, 768)

            _load_css(self.get_display())

            # Header
            header = Gtk.HeaderBar()
            header.set_show_title_buttons(True)

            title_label = Gtk.Label(label="Worklog")
            header.set_title_widget(title_label)

            search_entry = Gtk.SearchEntry()
            search_entry.set_placeholder_text("Search logs…")
            search_entry.set_hexpand(True)

            self._month_lbl = Gtk.Label(label="Month")

            prev_btn = Gtk.Button()
            prev_btn.set_child(Gtk.Image.new_from_icon_name("go-previous-symbolic"))
            next_btn = Gtk.Button()
            next_btn.set_child(Gtk.Image.new_from_icon_name("go-next-symbolic"))

            month_box = Gtk.Box(spacing=4)
            month_box.append(prev_btn)
            month_box.append(self._month_lbl)
            month_box.append(next_btn)

            logout_btn = Gtk.Button()
            logout_btn.set_child(Gtk.Image.new_from_icon_name("system-log-out-symbolic"))
            logout_btn.connect("clicked", self.on_logout)

            header.pack_start(month_box)
            header.pack_end(logout_btn)
            header.pack_end(search_entry)
            self.set_titlebar(header)

            # FlowBox grid
            self._flow = Gtk.FlowBox()
            self._flow.set_valign(Gtk.Align.START)
            self._flow.set_selection_mode(Gtk.SelectionMode.NONE)
            self._flow.set_max_children_per_line(4)
            self._flow.set_row_spacing(12)
            self._flow.set_column_spacing(12)

            scrolled = Gtk.ScrolledWindow()
            scrolled.set_child(self._flow)
            self.set_child(scrolled)

            self.refresh()

        def on_logout(self, _btn: Gtk.Button) -> None:
            from .login_window import LoginWindow  # local import
            self.user_store.sign_out()
            win = LoginWindow(application=self.get_application())
            win.present()
            self.close()

        def refresh(self) -> None:
            """Fetch logs from API and rebuild the grid."""
            token = getattr(self.user_store, "token", None)
            if not token:
                return
            from ..services import api_client
            try:
                logs = api_client.get_worklogs(token, sign_out=self._handle_sign_out) or []
            except Exception:
                return

            if not isinstance(logs, Iterable):
                return

            groups: dict[_dt.date, list[Mapping[str, Any]]] = defaultdict(list)
            for rec in logs:
                rt = rec.get("record_time")
                if rt:
                    s = str(rt)
                    try:
                        dt = _dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
                        d = dt.date()
                    except Exception:
                        try:
                            d = _dt.date.fromisoformat(s[:10])
                        except Exception:
                            d = _dt.date.today()
                else:
                    d = _dt.date.today()
                groups[d].append(rec)

            # clear existing
            child = self._flow.get_first_child()
            while child:
                next_child = child.get_next_sibling()
                self._flow.remove(child)
                child = next_child

            # newest first
            from .day_card import DayCard  # local import
            for d in sorted(groups.keys(), reverse=True):
                self._flow.append(DayCard(d, groups[d]))

            # update month label
            newest = max(groups.keys()) if groups else _dt.date.today()
            self._month_lbl.set_text(newest.strftime("%b %Y"))

        def _handle_sign_out(self) -> None:
            from .login_window import LoginWindow  # local import
            self.user_store.sign_out()
            win = LoginWindow(application=self.get_application())
            win.present()
            self.close()

else:  # pragma: no cover
    class MainWindow:  # type: ignore[misc]
        def __init__(self, *_args, **_kwargs):
            raise RuntimeError("GTK not available")


__all__ = ["MainWindow"]
