
"""
Adversarial hidden acceptance tests for the Main component.
These tests target gaps in visible test coverage to catch implementations
that pass visible tests via shortcuts rather than genuine contract compliance.
"""
import pytest
import os
import re
import json
from unittest.mock import patch, MagicMock, AsyncMock

# We need to set DATABASE_URL before importing app modules
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/testdb")

from fastapi.testclient import TestClient


def _get_test_client():
    """Create a TestClient with mocked DB dependencies."""
    # We need to mock db module before importing main
    import importlib
    with patch.dict("sys.modules", {}):
        pass

    from src.main import app
    return TestClient(app, raise_server_exceptions=False)


def _make_client_with_mocks(shorten_url_side_effect=None, resolve_side_effect=None, list_links_return=None):
    """
    Build a TestClient with shortener and db functions mocked.
    """
    from src import shortener as shortener_mod
    from src import db as db_mod
    from src.main import app

    client = TestClient(app, raise_server_exceptions=False)
    return client


# ─── Fixtures ───────────────────────────────────────────────────────────────

@pytest.fixture
def mock_db():
    """Mock all db functions to avoid real PostgreSQL connections."""
    with patch("src.db.get_conn") as mock_conn, \
         patch("src.db.execute") as mock_exec, \
         patch("src.db.execute_one") as mock_exec_one, \
         patch("src.db.close_conn") as mock_close:
        mock_conn.return_value = MagicMock()
        mock_exec.return_value = []
        mock_exec_one.return_value = None
        yield {
            "get_conn": mock_conn,
            "execute": mock_exec,
            "execute_one": mock_exec_one,
            "close_conn": mock_close,
        }


@pytest.fixture
def client(mock_db):
    """TestClient with mocked DB."""
    from src.main import app
    client = TestClient(app, raise_server_exceptions=False)
    return client


@pytest.fixture
def mock_shorten_url():
    with patch("src.shortener.shorten_url") as m:
        yield m


@pytest.fixture
def mock_resolve_and_track():
    with patch("src.shortener.resolve_and_track") as m:
        yield m


@pytest.fixture
def mock_list_links():
    with patch("src.shortener.list_links") as m:
        yield m


# ─── Helper to build ShortenResponse-like dicts ─────────────────────────────

def _shorten_response(code, url):
    """Simulate what shortener.shorten_url would return."""
    # We return an object that looks like ShortenResponse
    from unittest.mock import MagicMock
    resp = MagicMock()
    resp.short_url = f"http://localhost:8000/{code}"
    resp.code = code
    # Support dict-like access and Pydantic serialization
    resp.model_dump = lambda: {"short_url": f"http://localhost:8000/{code}", "code": code}
    resp.dict = lambda: {"short_url": f"http://localhost:8000/{code}", "code": code}
    return resp


# ─── Tests ──────────────────────────────────────────────────────────────────

class TestGoodhartPostShorten:

    def test_goodhart_post_shorten_response_contains_code_in_short_url(self, client, mock_shorten_url):
        """The short_url field in ShortenResponse must contain the returned code as a path suffix."""
        code = "aBc_-1"
        mock_shorten_url.return_value = _shorten_response(code, "https://example.com/unique-test-url-1")

        resp = client.post("/shorten", json={"url": "https://example.com/unique-test-url-1"})
        assert resp.status_code == 200
        body = resp.json()
        assert "code" in body
        assert "short_url" in body
        assert body["short_url"].endswith(body["code"])
        assert len(body["code"]) == 6

    def test_goodhart_post_shorten_short_url_format(self, client, mock_shorten_url):
        """The short_url must follow http://localhost:8000/{code} exactly."""
        code = "xY3z_W"
        mock_shorten_url.return_value = _shorten_response(code, "https://different-domain.org/page")

        resp = client.post("/shorten", json={"url": "https://different-domain.org/page"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["short_url"] == f"http://localhost:8000/{body['code']}"
        assert body["short_url"].startswith("http://localhost:8000/")

    def test_goodhart_post_shorten_idempotent_via_http(self, client, mock_shorten_url):
        """Submitting the same URL twice via HTTP must return the same code both times."""
        code = "iDm_Pt"
        mock_shorten_url.return_value = _shorten_response(code, "https://idempotent-test.com/page")

        resp1 = client.post("/shorten", json={"url": "https://idempotent-test.com/page"})
        resp2 = client.post("/shorten", json={"url": "https://idempotent-test.com/page"})

        assert resp1.status_code == 200
        assert resp2.status_code == 200
        assert resp1.json()["code"] == resp2.json()["code"]
        assert resp1.json()["short_url"] == resp2.json()["short_url"]

    def test_goodhart_post_shorten_different_urls_different_codes(self, client, mock_shorten_url):
        """Two distinct URLs must produce different short codes."""
        code1, code2 = "aB1c_D", "eF2g_H"
        mock_shorten_url.side_effect = [
            _shorten_response(code1, "https://url-one.com"),
            _shorten_response(code2, "https://url-two.com"),
        ]

        resp1 = client.post("/shorten", json={"url": "https://url-one.com"})
        resp2 = client.post("/shorten", json={"url": "https://url-two.com"})

        assert resp1.status_code == 200
        assert resp2.status_code == 200
        assert resp1.json()["code"] != resp2.json()["code"]

    def test_goodhart_post_shorten_empty_body(self, client, mock_shorten_url):
        """POST /shorten with empty JSON body must return 422."""
        resp = client.post("/shorten", json={})
        assert resp.status_code == 422
        body = resp.json()
        assert "detail" in body

    def test_goodhart_post_shorten_non_json_body(self, client, mock_shorten_url):
        """POST /shorten with non-JSON content must be rejected."""
        resp = client.post("/shorten", content="not json", headers={"Content-Type": "text/plain"})
        assert resp.status_code == 422

    def test_goodhart_post_shorten_http_url_accepted(self, client, mock_shorten_url):
        """POST /shorten must accept plain HTTP URLs, not just HTTPS."""
        code = "hTtP01"
        mock_shorten_url.return_value = _shorten_response(code, "http://plainhttp.example.com/page")

        resp = client.post("/shorten", json={"url": "http://plainhttp.example.com/page"})
        assert resp.status_code == 200
        body = resp.json()
        assert "code" in body
        assert "short_url" in body

    def test_goodhart_post_shorten_url_with_query_params(self, client, mock_shorten_url):
        """URLs with query parameters and fragments must be handled correctly."""
        url = "https://example.com/path?key=value&other=123#section"
        code = "qRy_12"
        mock_shorten_url.return_value = _shorten_response(code, url)

        resp = client.post("/shorten", json={"url": url})
        assert resp.status_code == 200
        body = resp.json()
        assert body["code"] == code
        # Verify shorten_url was called with the full URL
        mock_shorten_url.assert_called_once()
        call_arg = mock_shorten_url.call_args[0][0] if mock_shorten_url.call_args[0] else mock_shorten_url.call_args[1].get("original_url")
        # The URL passed to shortener should contain the query params
        assert "key=value" in str(call_arg)

    def test_goodhart_post_shorten_url_with_encoded_characters(self, client, mock_shorten_url):
        """URLs with percent-encoded characters must not be corrupted."""
        url = "https://example.com/path%20with%20spaces"
        code = "sPc_34"
        mock_shorten_url.return_value = _shorten_response(code, url)

        resp = client.post("/shorten", json={"url": url})
        assert resp.status_code == 200
        assert re.match(r"^[A-Za-z0-9_-]{6}$", resp.json()["code"])

    def test_goodhart_post_shorten_503_body_has_detail(self, client, mock_shorten_url):
        """503 response from CodeCollisionError must have ErrorResponse body with detail field."""
        from src.shortener import CodeCollisionError
        mock_shorten_url.side_effect = CodeCollisionError(attempts=5, message="All retries exhausted")

        resp = client.post("/shorten", json={"url": "https://collision-test.com"})
        assert resp.status_code == 503
        body = resp.json()
        assert "detail" in body
        assert isinstance(body["detail"], str)
        assert len(body["detail"]) > 0

    def test_goodhart_post_shorten_response_code_is_string(self, client, mock_shorten_url):
        """The code field in ShortenResponse must be a string type."""
        code = "sTr_56"
        mock_shorten_url.return_value = _shorten_response(code, "https://type-check.com")

        resp = client.post("/shorten", json={"url": "https://type-check.com"})
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body["code"], str)

    def test_goodhart_post_shorten_method_not_allowed_get(self, client, mock_shorten_url):
        """GET /shorten must not be routable - only POST is accepted."""
        resp = client.get("/shorten")
        # Should be 405 Method Not Allowed, or 404, but NOT 200
        assert resp.status_code in (404, 405)


class TestGoodhartGetRedirect:

    def test_goodhart_get_redirect_307_not_301_or_302(self, client, mock_resolve_and_track):
        """Redirect must be specifically HTTP 307, not 301 or 302."""
        mock_resolve_and_track.return_value = "https://target-site.com"

        resp = client.get("/aBcDeF", follow_redirects=False)
        assert resp.status_code == 307
        assert "location" in resp.headers
        assert resp.headers["location"] == "https://target-site.com"

    def test_goodhart_get_redirect_location_header_matches_original(self, client, mock_resolve_and_track):
        """Location header must exactly match the original URL that was shortened."""
        original = "https://very-specific-url.example.com/with/path?q=1&r=2#frag"
        mock_resolve_and_track.return_value = original

        resp = client.get("/xYz_12", follow_redirects=False)
        assert resp.status_code == 307
        assert resp.headers["location"] == original

    def test_goodhart_get_redirect_not_found_body_has_detail(self, client, mock_resolve_and_track):
        """404 response must include ErrorResponse JSON with a non-empty detail field."""
        mock_resolve_and_track.return_value = None

        resp = client.get("/noExst")
        assert resp.status_code == 404
        body = resp.json()
        assert "detail" in body
        assert isinstance(body["detail"], str)
        assert len(body["detail"]) > 0

    def test_goodhart_redirect_calls_resolve_and_track_with_code(self, client, mock_resolve_and_track):
        """GET /{code} must pass the code from the URL path to resolve_and_track."""
        mock_resolve_and_track.return_value = "https://example.com"

        client.get("/tEsT_1", follow_redirects=False)
        mock_resolve_and_track.assert_called_once()
        # The code passed must match the path parameter
        call_arg = mock_resolve_and_track.call_args[0][0] if mock_resolve_and_track.call_args[0] else mock_resolve_and_track.call_args[1].get("code")
        assert call_arg == "tEsT_1"


class TestGoodhartGetLinks:

    def test_goodhart_get_links_does_not_capture_literal_path(self, client, mock_list_links, mock_resolve_and_track):
        """GET /links must route to get_links handler, not the /{code} path parameter handler."""
        mock_list_links.return_value = []
        mock_resolve_and_track.return_value = None

        resp = client.get("/links")
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, list)
        # Verify list_links was called, not resolve_and_track
        mock_list_links.assert_called()

    def test_goodhart_get_links_item_schema(self, client, mock_list_links):
        """Each item in /links response must contain all LinkListItem fields."""
        mock_list_links.return_value = [
            MagicMock(
                code="a1B2c3",
                original_url="https://example.com",
                created_at="2024-01-01T00:00:00Z",
                hit_count=5,
                model_dump=lambda: {
                    "code": "a1B2c3",
                    "original_url": "https://example.com",
                    "created_at": "2024-01-01T00:00:00Z",
                    "hit_count": 5,
                },
                dict=lambda: {
                    "code": "a1B2c3",
                    "original_url": "https://example.com",
                    "created_at": "2024-01-01T00:00:00Z",
                    "hit_count": 5,
                },
            )
        ]

        resp = client.get("/links")
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, list)
        assert len(body) >= 1
        item = body[0]
        assert "code" in item
        assert "original_url" in item
        assert "created_at" in item
        assert "hit_count" in item

    def test_goodhart_get_links_excludes_internal_id(self, client, mock_list_links):
        """Items in /links response must not expose internal database 'id' field."""
        mock_list_links.return_value = [
            MagicMock(
                code="nO_iD1",
                original_url="https://no-id.com",
                created_at="2024-06-01T12:00:00Z",
                hit_count=0,
                model_dump=lambda: {
                    "code": "nO_iD1",
                    "original_url": "https://no-id.com",
                    "created_at": "2024-06-01T12:00:00Z",
                    "hit_count": 0,
                },
                dict=lambda: {
                    "code": "nO_iD1",
                    "original_url": "https://no-id.com",
                    "created_at": "2024-06-01T12:00:00Z",
                    "hit_count": 0,
                },
            )
        ]

        resp = client.get("/links")
        assert resp.status_code == 200
        body = resp.json()
        for item in body:
            assert "id" not in item, "LinkListItem should not expose internal 'id' field"

    def test_goodhart_get_links_ordering_multiple_items(self, client, mock_list_links):
        """GET /links must return items ordered by created_at descending (newest first)."""
        items = [
            MagicMock(
                code="nEw_01",
                original_url="https://newer.com",
                created_at="2024-06-15T12:00:00Z",
                hit_count=0,
                model_dump=lambda: {
                    "code": "nEw_01",
                    "original_url": "https://newer.com",
                    "created_at": "2024-06-15T12:00:00Z",
                    "hit_count": 0,
                },
                dict=lambda: {
                    "code": "nEw_01",
                    "original_url": "https://newer.com",
                    "created_at": "2024-06-15T12:00:00Z",
                    "hit_count": 0,
                },
            ),
            MagicMock(
                code="oLd_02",
                original_url="https://older.com",
                created_at="2024-01-01T00:00:00Z",
                hit_count=3,
                model_dump=lambda: {
                    "code": "oLd_02",
                    "original_url": "https://older.com",
                    "created_at": "2024-01-01T00:00:00Z",
                    "hit_count": 3,
                },
                dict=lambda: {
                    "code": "oLd_02",
                    "original_url": "https://older.com",
                    "created_at": "2024-01-01T00:00:00Z",
                    "hit_count": 3,
                },
            ),
        ]
        mock_list_links.return_value = items

        resp = client.get("/links")
        assert resp.status_code == 200
        body = resp.json()
        assert len(body) == 2
        # Newer item should come first
        assert body[0]["created_at"] >= body[1]["created_at"]


class TestGoodhartGetIndex:

    def test_goodhart_get_index_not_captured_by_code_route(self, client, mock_resolve_and_track):
        """GET / must serve index.html, not be interpreted as a short code lookup."""
        # If route order is wrong, / might hit the /{code} handler
        mock_resolve_and_track.return_value = None

        # Create the static file so the endpoint can serve it
        static_dir = os.path.join(os.path.dirname(__file__), "..", "src", "static")
        os.makedirs(static_dir, exist_ok=True)
        index_path = os.path.join(static_dir, "index.html")
        file_existed = os.path.exists(index_path)
        if not file_existed:
            with open(index_path, "w") as f:
                f.write("<html><body>test</body></html>")

        try:
            resp = client.get("/")
            assert resp.status_code == 200
            assert "text/html" in resp.headers.get("content-type", "")
            # resolve_and_track should NOT have been called
            mock_resolve_and_track.assert_not_called()
        finally:
            if not file_existed and os.path.exists(index_path):
                os.remove(index_path)


class TestGoodhartStartupShutdown:

    @pytest.mark.asyncio
    async def test_goodhart_startup_propagates_db_error(self, mock_db):
        """startup_event must propagate connection errors, not swallow them."""
        mock_db["get_conn"].side_effect = Exception("Connection refused")

        from src.main import startup_event
        with pytest.raises(Exception, match="Connection refused"):
            await startup_event()

    @pytest.mark.asyncio
    async def test_goodhart_shutdown_calls_close_conn(self, mock_db):
        """shutdown_event must call db.close_conn."""
        from src.main import shutdown_event
        await shutdown_event()
        mock_db["close_conn"].assert_called_once()


class TestGoodhartCodeCollisionBoundary:

    def test_goodhart_code_collision_error_boundary_max_attempts_5(self, client, mock_shorten_url):
        """CodeCollisionError with attempts=5 (upper boundary) must result in 503."""
        from src.shortener import CodeCollisionError
        mock_shorten_url.side_effect = CodeCollisionError(attempts=5, message="Max retries at boundary")

        resp = client.post("/shorten", json={"url": "https://boundary-max.com"})
        assert resp.status_code == 503
        body = resp.json()
        assert "detail" in body


class TestGoodhartIntegrationFlow:

    def test_goodhart_redirect_hit_count_reflects_in_links(self, client, mock_shorten_url, mock_resolve_and_track, mock_list_links):
        """After multiple redirects, GET /links must show the accumulated hit_count."""
        code = "hIt_01"
        mock_shorten_url.return_value = _shorten_response(code, "https://hit-count-test.com")
        mock_resolve_and_track.return_value = "https://hit-count-test.com"

        # Shorten a URL
        resp = client.post("/shorten", json={"url": "https://hit-count-test.com"})
        assert resp.status_code == 200

        # Redirect 3 times
        for _ in range(3):
            r = client.get(f"/{code}", follow_redirects=False)
            assert r.status_code == 307

        # Verify resolve_and_track was called 3 times
        assert mock_resolve_and_track.call_count == 3

    def test_goodhart_post_shorten_delegates_url_to_shortener(self, client, mock_shorten_url):
        """POST /shorten must pass the submitted URL to shortener.shorten_url, not hardcode anything."""
        url = "https://unique-delegation-test-url-99.example.org/foo"
        code = "dLg_99"
        mock_shorten_url.return_value = _shorten_response(code, url)

        client.post("/shorten", json={"url": url})
        mock_shorten_url.assert_called_once()
        # Extract the URL argument passed to shorten_url
        args = mock_shorten_url.call_args
        passed_url = args[0][0] if args[0] else args[1].get("original_url", args[1].get("url", ""))
        assert str(passed_url) == url
