from __future__ import annotations

"""
DayCard widget: shows a single day's worklog entries in a card layout suitable
for placement inside a Gtk.FlowBox (wrapping grid).  Designed to match the
multi-column card look in the screenshot spec.

We pass raw log dicts (each with at least ``record_time`` and ``content``) so
callers don't need to build intermediate GObject models.
"""

import datetime as _dt
from typing import Iterable, Mapping, Any

try:
    import gi  # type: ignore
    gi.require_version("Gtk", "4.0")
    gi.require_version("Pango", "1.0")
    from gi.repository import Gtk, Pango
except Exception:  # pragma: no cover - gi not installed
    Gtk = Pango = None  # type: ignore


def _coerce_time_str(record_time: Any) -> str:
    """Return HH:MM best-effort from a backend ``record_time`` field."""
    if not record_time:
        return ""
    s = str(record_time)
    try:
        dt = _dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:  # degrade gracefully
        return s[11:16] if len(s) >= 16 else s
    return dt.strftime("%H:%M")


if Gtk:

    class LogEntryRow(Gtk.Box):  # pragma: no cover - pure UI glue
        def __init__(self, time_str: str, text: str) -> None:
            super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            self.add_css_class("log-entry-row")
            self.set_margin_top(2)
            self.set_margin_bottom(2)

            time_label = Gtk.Label(label=time_str, xalign=0)
            time_label.set_width_chars(5)
            time_label.add_css_class("log-entry-time")
            self.append(time_label)

            text_label = Gtk.Label(label=text, xalign=0)
            text_label.add_css_class("log-entry-text")
            text_label.set_wrap(True)
            text_label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
            text_label.set_hexpand(True)
            self.append(text_label)


    class DayCard(Gtk.FlowBoxChild):  # pragma: no cover - pure UI glue
        def __init__(self, date_obj: _dt.date, logs: Iterable[Mapping[str, Any]]) -> None:
            super().__init__()

            frame = Gtk.Frame()
            frame.add_css_class("day-card")
            frame.set_margin_top(8)
            frame.set_margin_bottom(8)
            frame.set_margin_start(8)
            frame.set_margin_end(8)

            outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            outer.set_margin_top(8)
            outer.set_margin_bottom(8)
            outer.set_margin_start(12)
            outer.set_margin_end(12)

            # Header: date + DOW
            header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            date_lbl = Gtk.Label(label=date_obj.strftime("%m/%d"), xalign=0)
            date_lbl.add_css_class("day-card-header")
            dow_lbl = Gtk.Label(label=date_obj.strftime("%a").upper(), xalign=1)
            dow_lbl.add_css_class("dim-label")
            header_box.append(date_lbl)
            header_box.append(dow_lbl)
            outer.append(header_box)

            sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
            sep.add_css_class("day-card-separator")
            outer.append(sep)

            for rec in logs:
                time_str = _coerce_time_str(rec.get("record_time"))
                text = str(rec.get("content", ""))
                outer.append(LogEntryRow(time_str, text))

            frame.set_child(outer)
            self.set_child(frame)

else:  # pragma: no cover - non-GTK runtime
    class DayCard:  # type: ignore[misc]
        def __init__(self, *_args, **_kwargs) -> None:
            raise RuntimeError("GTK not available")


__all__ = ["DayCard"]
