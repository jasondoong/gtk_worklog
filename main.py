#!/usr/bin/env python3
"""Entry point for the Worklog desktop application."""

from worklog.app import WorklogApplication


def main() -> None:
    app = WorklogApplication()
    app.run()


if __name__ == "__main__":
    main()
