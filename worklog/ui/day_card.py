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
        def __init__(self, time_str: str, text: str, on_edit=None, get_token=None) -> None:
            super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            self.add_css_class("log-entry-row")
            self.set_margin_top(2)
            self.set_margin_bottom(2)
            self.on_edit = on_edit
            self._editing = False
            self._orig_text = text
            self._time_str = time_str
            self._get_token = get_token  # 新增：token getter

            self.time_label = Gtk.Label(label=time_str, xalign=0)
            self.time_label.set_width_chars(5)
            self.time_label.add_css_class("log-entry-time")
            self.append(self.time_label)

            self.text_label = Gtk.Label(label=text, xalign=0)
            self.text_label.add_css_class("log-entry-text")
            self.text_label.set_wrap(True)
            self.text_label.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
            self.text_label.set_hexpand(False)  # 防止撐開父層寬度
            self.text_label.set_halign(Gtk.Align.FILL)
            self.text_label.set_max_width_chars(42)  # 強制最大寬度
            self.text_label.set_ellipsize(Pango.EllipsizeMode.NONE)  # 不要省略號，強制換行
            self.append(self.text_label)

            # 新增：點擊文字可編輯
            click_controller = Gtk.GestureClick()
            click_controller.set_button(0)  # 0 代表任何滑鼠鍵
            click_controller.connect("released", self._on_text_clicked)
            self.text_label.add_controller(click_controller)

        def _on_text_clicked(self, gesture, n_press, x, y):
            if n_press == 1 and not self._editing:
                self._show_edit_dialog()

        def _show_edit_dialog(self):
            self._editing = True
            parent_win = self.get_root()
            dialog = Gtk.Dialog(title="編輯內容", transient_for=parent_win, modal=True)
            dialog.set_default_size(400, 320)
            box = dialog.get_content_area()
            box.set_margin_top(16)
            box.set_margin_bottom(16)
            box.set_margin_start(16)
            box.set_margin_end(16)
            # 改用 TextView
            # 用 ScrolledWindow 包住 TextView，避免內容過多時擠掉按鈕
            scrolled = Gtk.ScrolledWindow()
            scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            scrolled.set_min_content_height(120)
            scrolled.set_max_content_height(220)
            scrolled.set_hexpand(True)
            scrolled.set_vexpand(True)
            textview = Gtk.TextView()
            textview.set_wrap_mode(Pango.WrapMode.WORD_CHAR)
            textview.set_vexpand(True)
            textview.set_hexpand(True)
            buffer = textview.get_buffer()
            buffer.set_text(self._orig_text)
            scrolled.set_child(textview)
            box.append(scrolled)
            btn_save = Gtk.Button.new_with_label("儲存")
            btn_cancel = Gtk.Button.new_with_label("取消")
            btn_delete = Gtk.Button.new_with_label("刪除")
            btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            btn_box.set_margin_top(16)
            btn_box.set_vexpand(False)
            btn_box.set_hexpand(True)
            btn_box.append(btn_save)
            btn_box.append(btn_cancel)
            btn_box.append(btn_delete)
            box.append(btn_box)
            dialog.connect("close-request", lambda *_: self._set_editing_false())
            def on_save(_btn):
                start, end = buffer.get_bounds()
                new_text = buffer.get_text(start, end, True)
                if new_text != self._orig_text:
                    if self.on_edit:
                        import threading
                        def do_patch():
                            from worklog.services import api_client
                            rec = getattr(self, '_rec', None)
                            token = self._get_token() if self._get_token else getattr(self, '_token', None)
                            if rec and token:
                                try:
                                    api_client.update_worklog(
                                        token=token,
                                        worklog_id=rec['id'],
                                        content=new_text,
                                        record_time=rec.get('record_time'),
                                        tag_id=rec.get('tag_id'),
                                    )
                                except Exception:
                                    pass  # 可加上錯誤提示
                            # UI 更新必須回到主執行緒
                            import gi
                            from gi.repository import GLib
                            GLib.idle_add(lambda: self.on_edit(self._time_str, new_text))
                        threading.Thread(target=do_patch, daemon=True).start()
                    self.text_label.set_text(new_text)
                    self._orig_text = new_text
                self._editing = False
                dialog.close()
            def on_delete(_btn):
                import threading
                def do_delete():
                    from worklog.services import api_client
                    rec = getattr(self, '_rec', None)
                    token = self._get_token() if self._get_token else getattr(self, '_token', None)
                    if rec and token:
                        try:
                            api_client.delete_worklog(token=token, worklog_id=rec['id'])
                        except Exception:
                            pass  # 可加上錯誤提示
                    # UI 更新必須回到主執行緒
                    import gi
                    from gi.repository import GLib
                    GLib.idle_add(lambda: self.on_edit(self._time_str, None))
                threading.Thread(target=do_delete, daemon=True).start()
                self._editing = False
                dialog.close()
            def on_cancel(_btn):
                self._editing = False
                dialog.close()
            def _set_editing_false():
                self._editing = False
            self._set_editing_false = _set_editing_false
            btn_save.connect("clicked", on_save)
            btn_cancel.connect("clicked", on_cancel)
            btn_delete.connect("clicked", on_delete)
            dialog.show()
            textview.grab_focus()

    class DayCard(Gtk.FlowBoxChild):  # pragma: no cover - pure UI glue
        def __init__(self, date_obj: _dt.date, logs: Iterable[dict], token: str = None, get_token=None) -> None:
            super().__init__()

            frame = Gtk.Frame()
            frame.add_css_class("day-card")
            frame.set_margin_top(8)
            frame.set_margin_bottom(8)
            frame.set_margin_start(8)
            frame.set_margin_end(8)
            if hasattr(frame, "set_max_width"):
                frame.set_max_width(220)

            outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            outer.set_margin_top(8)
            outer.set_margin_bottom(8)
            outer.set_margin_start(12)
            outer.set_margin_end(12)
            outer.set_hexpand(False)
            outer.set_halign(Gtk.Align.FILL)

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

            self._log_rows = []  # 新增：記錄 row 物件
            for rec in logs:
                time_str = _coerce_time_str(rec.get("record_time"))
                text = str(rec.get("content", ""))
                def on_edit(time_str, new_text, rec=rec, row_ref=None):
                    if new_text is None:
                        # 刪除：移除 row
                        if row_ref and row_ref in self._log_rows:
                            outer.remove(row_ref)
                            self._log_rows.remove(row_ref)
                        rec["_deleted"] = True
                    else:
                        rec["content"] = new_text
                        # 可加上通知父元件或觸發資料儲存的邏輯
                row = LogEntryRow(time_str, text, on_edit=None, get_token=get_token)
                row._rec = rec  # 傳遞 rec 給 LogEntryRow 以便 PATCH/DELETE
                # row._token = token  # 不再直接傳 token，改用 get_token
                # 綁定 on_edit 並傳遞 row 參考
                import functools
                row.on_edit = functools.partial(on_edit, rec=rec, row_ref=row)
                self._log_rows.append(row)
                outer.append(row)

            frame.set_child(outer)
            self.set_child(frame)

else:  # pragma: no cover - non-GTK runtime
    class DayCard:  # type: ignore[misc]
        def __init__(self, *_args, **_kwargs) -> None:
            raise RuntimeError("GTK not available")


__all__ = ["DayCard"]
