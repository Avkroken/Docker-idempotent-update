"""Minimal stdlib-only Sentry error reporter.

No sentry-sdk (third-party package) — the repo's convention allows only
stdlib. Posts unhandled exceptions directly to Sentry's envelope API
(`<host>/api/<project_id>/envelope/`) via urllib, authenticated with
the `X-Sentry-Auth` header and the public key from the DSN.

DSN is read from the `SENTRY_DSN` environment variable — no-op if absent.
"""

import json
import os
import re
import time
import traceback
import urllib.error
import urllib.parse
import urllib.request
import uuid

# Redaction patterns and logic adapted from github_report.py
_SECRET_ENV_MARKERS = ("KEY", "TOKEN", "SECRET", "PASSWORD", "PASS")
_EMAIL_RE = re.compile(r"[\w.+-]{1,64}@[\w.-]{1,255}\.\w{2,24}")
_HOME_PATH_RE = re.compile(r"/home/[^/\s]+")
_KEY_PATTERN_RE = re.compile(
    r"(sk-[A-Za-z0-9]{16,}|ghp_[A-Za-z0-9]{20,}|gho_[A-Za-z0-9]{20,}|"
    r"AKIA[A-Z0-9]{12,}|Bearer\s+[A-Za-z0-9._-]{10,})"
)


def _redact(text: str) -> str:
    """Redacts secrets, emails, and local paths from text."""
    for key, value in os.environ.items():
        if (
            value
            and len(value) >= 8
            and any(m in key.upper() for m in _SECRET_ENV_MARKERS)
        ):
            text = text.replace(value, "[REDACTED]")
    text = _KEY_PATTERN_RE.sub("[REDACTED]", text)
    text = _EMAIL_RE.sub("[EMAIL REDACTED]", text)
    text = _HOME_PATH_RE.sub("/home/[user]", text)
    return text


def _parse_dsn(dsn: str) -> tuple[str, str] | None:
    """Returns (envelope_url, public_key) or None if the DSN is invalid."""
    parsed = urllib.parse.urlparse(dsn)
    if not parsed.hostname or not parsed.username or not parsed.path:
        return None
    project_id = parsed.path.strip("/")
    if not project_id:
        return None
    host = parsed.hostname
    if parsed.port:
        host = f"{host}:{parsed.port}"
    envelope_url = f"{parsed.scheme}://{host}/api/{project_id}/envelope/"
    return envelope_url, parsed.username


def report_error_to_sentry(exc: BaseException) -> None:
    """Sends an unhandled exception to Sentry. Best-effort — no-op if
    `SENTRY_DSN` is absent or if the network/DSN is broken, must never
    crash the caller."""
    dsn = os.environ.get("SENTRY_DSN")
    if not dsn:
        return

    parsed = _parse_dsn(dsn)
    if parsed is None:
        return
    envelope_url, public_key = parsed

    try:
        # Redact exception message and traceback filenames
        exc_value = _redact(str(exc))
        frames = []
        for f in traceback.extract_tb(exc.__traceback__):
            frames.append(
                {
                    "filename": _redact(f.filename),
                    "lineno": f.lineno,
                    "function": f.name,
                }
            )

        environment = os.environ.get("SENTRY_ENVIRONMENT", "production")

        event = {
            "event_id": uuid.uuid4().hex,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "platform": "python",
            "environment": environment,
            "exception": {
                "values": [
                    {
                        "type": type(exc).__name__,
                        "value": exc_value,
                        "stacktrace": {"frames": frames},
                    }
                ]
            },
        }

        # Sentry envelope format: header line + item header line + item payload
        event_json = json.dumps(event)
        envelope_header = json.dumps({"event_id": event["event_id"]})
        item_header = json.dumps({"type": "event", "content_type": "application/json"})
        envelope_body = f"{envelope_header}\n{item_header}\n{event_json}\n"

        headers = {
            "Content-Type": "application/x-sentry-envelope",
            "X-Sentry-Auth": (
                "Sentry sentry_version=7, sentry_client=docker-idempotent-update/1.0, "
                f"sentry_key={public_key}"
            ),
        }

        req = urllib.request.Request(
            envelope_url, data=envelope_body.encode(), headers=headers, method="POST"
        )
        with urllib.request.urlopen(req, timeout=15):
            pass
    except (urllib.error.URLError, OSError, Exception):
        # Best-effort: swallow all exceptions to never crash the caller
        pass
