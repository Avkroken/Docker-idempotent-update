"""Minimal stdlib-only Sentry error reporter.

Ingen sentry-sdk (tredjepartspaket) — repots konvention tillåter bara
stdlib. Postar ohanterade undantag direkt mot Sentrys äldre "store"-API
(`<host>/api/<project_id>/store/`) via urllib, autentiserat med
`X-Sentry-Auth`-headern och den publika nyckeln ur DSN:en.

DSN läses från `SENTRY_DSN`-env-variabeln — no-op om den saknas.
"""

import json
import os
import time
import traceback
import urllib.error
import urllib.parse
import urllib.request
import uuid


def _parse_dsn(dsn: str) -> tuple[str, str] | None:
    """Returnerar (store_url, public_key) eller None om DSN:en är ogiltig."""
    parsed = urllib.parse.urlparse(dsn)
    if not parsed.hostname or not parsed.username or not parsed.path:
        return None
    project_id = parsed.path.strip("/")
    if not project_id:
        return None
    store_url = f"{parsed.scheme}://{parsed.hostname}/api/{project_id}/store/"
    return store_url, parsed.username


def report_error_to_sentry(exc: BaseException) -> None:
    """Skickar ett ohanterat undantag till Sentry. Best-effort — no-op om
    `SENTRY_DSN` saknas eller nätverket/DSN:en är trasig, ska aldrig
    krascha anroparen."""
    dsn = os.environ.get("SENTRY_DSN")
    if not dsn:
        return

    parsed = _parse_dsn(dsn)
    if parsed is None:
        return
    store_url, public_key = parsed

    event = {
        "event_id": uuid.uuid4().hex,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "platform": "python",
        "exception": {
            "values": [
                {
                    "type": type(exc).__name__,
                    "value": str(exc),
                    "stacktrace": {
                        "frames": [
                            {
                                "filename": f.filename,
                                "lineno": f.lineno,
                                "function": f.name,
                            }
                            for f in traceback.extract_tb(exc.__traceback__)
                        ]
                    },
                }
            ]
        },
    }

    headers = {
        "Content-Type": "application/json",
        "X-Sentry-Auth": (
            "Sentry sentry_version=7, sentry_client=docker-idempotent-update/1.0, "
            f"sentry_key={public_key}"
        ),
    }

    try:
        req = urllib.request.Request(
            store_url, data=json.dumps(event).encode(), headers=headers, method="POST"
        )
        with urllib.request.urlopen(req, timeout=15):
            pass
    except (urllib.error.URLError, OSError):
        pass
