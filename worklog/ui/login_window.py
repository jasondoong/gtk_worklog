"""Login window – Google sign-in entry point."""

import logging

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

    class LoginWindow(Gtk.ApplicationWindow):  # pragma: no cover - UI code
        """Simple login window with Google sign-in only."""

        def __init__(self, **kwargs):
            super().__init__(**kwargs)

            self.set_title("Worklog • Sign in")
            self.set_default_size(400, 200)

            # Header bar
            header = Gtk.HeaderBar()
            header.set_show_title_buttons(True)
            title_label = Gtk.Label(label="Worklog • Sign in")
            header.set_title_widget(title_label)
            self.set_titlebar(header)

            # Content area
            box = Gtk.Box(
                orientation=Gtk.Orientation.VERTICAL,
                spacing=12,
                margin_top=20,
            )
            box.set_halign(Gtk.Align.CENTER)
            box.set_valign(Gtk.Align.CENTER)

            google_btn = Gtk.Button(label="Google")
            google_btn.connect("clicked", self.on_google)

            btn_box = Gtk.Box(spacing=12)
            btn_box.append(google_btn)
            box.append(btn_box)

            self.set_child(box)

        def on_google(self, _button: Gtk.Button) -> None:  # pragma: no cover - UI code
            """Run Google OAuth → exchange for Firebase → sign in."""
            from ..auth.firebase import load_firebase_config
            from ..auth.google import do_google_oauth, exchange_google_to_firebase

            app = self.get_application()  # type: ignore[assignment]

            try:
                # Step 1: Browser OAuth
                google_id_token, _google_refresh = do_google_oauth()

                # Step 2: Firebase exchange
                fb_cfg = load_firebase_config()
                api_key = fb_cfg["apiKey"]
                id_token, refresh_token = exchange_google_to_firebase(api_key, google_id_token)
            except Exception as exc:  # pragma: no cover - UI error path
                logging.exception("Google sign-in failed")
                self._show_error(f"Google sign-in failed:\n{exc}")
                return

            # Step 3: Persist + open main window
            app.user_store.sign_in(id_token, refresh_token)

            from .main_window import MainWindow
            win = MainWindow(app.user_store, application=app)
            app.main_window = win  # keep reference on the app
            win.present()
            self.close()

        def _show_error(self, message: str) -> None:  # pragma: no cover - UI code
            """Simple inline error dialog."""
            dlg = Adw.MessageDialog.new(
                self,
                heading="Sign-in error",
                body=message,
            )
            dlg.add_response("ok", "OK")
            dlg.set_default_response("ok")
            dlg.connect("response", lambda *_: dlg.destroy())
            dlg.present()

else:
    class LoginWindow:  # type: ignore[misc]
        pass
