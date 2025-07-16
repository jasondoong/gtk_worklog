# gtk_worklog

A GTK desktop client for Worklog.

## Installation

```bash
poetry install
```

## Running Tests

```bash
pytest
```

## Configuration

The application expects Firebase and Google OAuth settings. By default it reads:

* `~/.config/worklog/firebase_config.json`
* `~/.config/worklog/google_oauth_client.json`

Individual values may also be provided via environment variables with the
`WORKLOG_` prefix, for example `WORKLOG_FB_API_KEY` or
`WORKLOG_GOOGLE_CLIENT_ID`.

