import importlib.util
import os
from pathlib import Path

import pytest
import requests

os.environ.setdefault("PLEX_TOKEN", "synthetic-test-token")
MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "plex-clear-watchlist"
    / "plex_clear_watchlist.py"
)
SPEC = importlib.util.spec_from_file_location("plex_clear_watchlist_test", MODULE_PATH)
plex = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(plex)


class FakeResponse:
    def __init__(self, payload=None, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(
                f"HTTP {self.status_code}",
                response=self,
            )


def test_missing_total_size_paginates_until_an_empty_page(monkeypatch):
    responses = [
        FakeResponse({"MediaContainer": {"Metadata": [{"ratingKey": "1"}]}}),
        FakeResponse({"MediaContainer": {"Metadata": [{"ratingKey": "2"}]}}),
        FakeResponse({"MediaContainer": {"Metadata": []}}),
    ]
    pages = []

    def fake_get(_url, **kwargs):
        pages.append(kwargs["params"]["page"])
        return responses.pop(0)

    monkeypatch.setattr(plex.requests, "get", fake_get)

    assert [item["ratingKey"] for item in plex.get_watchlist()] == ["1", "2"]
    assert pages == [1, 2, 3]


def test_known_total_size_fails_closed_if_pages_end_early(monkeypatch):
    responses = [
        FakeResponse(
            {
                "MediaContainer": {
                    "Metadata": [{"ratingKey": "1"}],
                    "totalSize": 2,
                }
            }
        ),
        FakeResponse({"MediaContainer": {"Metadata": [], "totalSize": 2}}),
    ]
    monkeypatch.setattr(
        plex.requests,
        "get",
        lambda *_args, **_kwargs: responses.pop(0),
    )

    with pytest.raises(requests.RequestException, match="1 av 2"):
        plex.get_watchlist()


def test_invalid_total_size_fails_closed(monkeypatch):
    response = FakeResponse(
        {
            "MediaContainer": {
                "Metadata": [{"ratingKey": "1"}],
                "totalSize": "unknown",
            }
        }
    )
    monkeypatch.setattr(
        plex.requests,
        "get",
        lambda *_args, **_kwargs: response,
    )

    with pytest.raises(requests.RequestException, match="ogiltig totalSize"):
        plex.get_watchlist()


def test_delete_rejects_missing_rating_key_without_http_request(monkeypatch):
    called = False

    def fake_delete(*_args, **_kwargs):
        nonlocal called
        called = True
        raise AssertionError("HTTP request must not run")

    monkeypatch.setattr(plex.requests, "delete", fake_delete)

    assert plex.delete_from_watchlist("   ", "Broken item") is False
    assert called is False


def test_delete_url_encodes_rating_key(monkeypatch):
    seen = {}

    def fake_delete(url, **kwargs):
        seen["url"] = url
        seen["headers"] = kwargs["headers"]
        return FakeResponse(status_code=204)

    monkeypatch.setattr(plex.requests, "delete", fake_delete)

    assert plex.delete_from_watchlist("abc/def?x=1", "Example") is True
    assert seen["url"].endswith("/abc%2Fdef%3Fx%3D1")


def test_selection_keeps_newest_before_applying_limit():
    items = [{"ratingKey": str(index)} for index in range(1, 7)]

    selected = plex._select_items(items, keep=2, limit=3)

    assert [item["ratingKey"] for item in selected] == ["1", "2", "3"]
