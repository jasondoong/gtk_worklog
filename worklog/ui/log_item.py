"""UI data models for log list items."""

try:
    import gi
    gi.require_version("GObject", "2.0")
    from gi.repository import GObject
    GI_AVAILABLE = True
except Exception:  # pragma: no cover - gi not installed
    GI_AVAILABLE = False

    class GObject:
        class Object:
            pass

        class Property:
            def __init__(self, **kwargs):
                pass

if GI_AVAILABLE:

    class DateHeader(GObject.Object):  # pragma: no cover - GTK specific
        """Represents a date header in the log list."""

        date = GObject.Property(type=str)

        def __init__(self, date: str) -> None:
            super().__init__()
            self.date = date


    class LogItem(GObject.Object):  # pragma: no cover - GTK specific
        """Represents a single log entry in the list."""

        time = GObject.Property(type=str)
        text = GObject.Property(type=str)

        def __init__(self, time: str, text: str) -> None:
            super().__init__()
            self.time = time
            self.text = text

else:

    class DateHeader:  # type: ignore[misc]
        def __init__(self, date: str):
            self.date = date

    class LogItem:  # type: ignore[misc]
        def __init__(self, time: str, text: str):
            self.time = time
            self.text = text
