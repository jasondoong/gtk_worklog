import os
import sys
from unittest.mock import MagicMock

# Ensure project root on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import main


def test_main_runs_application(monkeypatch):
    app_instance = MagicMock()
    monkeypatch.setattr(main, "WorklogApplication", lambda: app_instance)
    main.main()
    app_instance.run.assert_called_once()
