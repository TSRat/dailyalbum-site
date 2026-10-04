"""Serve the regional DailyAlbum site from an Alibaba Cloud FC HTTP trigger.

The code package contains a ``site`` directory and a compact CN-only IP range
snapshot. The request's FC ``sourceIp`` is used directly; forwarded headers are
intentionally ignored because callers can forge them.
"""

from __future__ import annotations

import base64
import bisect
import ipaddress
import json
import mimetypes
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit


HERE = Path(__file__).resolve().parent
SITE = HERE / "site"
APEX = "https://dailyalbumapp.com"
_ranges = json.loads((HERE / "cn_ranges.json").read_text(encoding="utf-8"))
_v4 = _ranges["ipv4"]
_v6 = _ranges["ipv6"]
_v4_starts = [row[0] for row in _v4]
_v6_starts = [row[0] for row in _v6]


def _is_mainland(source_ip: str) -> bool | None:
    try:
        ip = ipaddress.ip_address(source_ip)
    except ValueError:
        return None
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
        ip = ip.ipv4_mapped
    if not ip.is_global:
        return None
    rows, starts = (_v4, _v4_starts) if ip.version == 4 else (_v6, _v6_starts)
    value = int(ip)
    position = bisect.bisect_right(starts, value) - 1
    return position >= 0 and value <= rows[position][1]


def _response(status: int, body: bytes = b"", *, content_type: str = "text/plain; charset=utf-8",
              extra: dict[str, str] | None = None, head: bool = False) -> dict[str, Any]:
    headers = {
        "Content-Type": content_type,
        "X-Content-Type-Options": "nosniff",
        "Content-Length": str(len(body)),
    }
    if extra:
        headers.update(extra)
    binary = not content_type.startswith(("text/", "application/json", "application/javascript"))
    return {
        "statusCode": status,
        "headers": headers,
        "isBase64Encoded": binary and not head,
        "body": "" if head else (base64.b64encode(body).decode("ascii") if binary else body.decode("utf-8")),
    }


def _redirect(path: str) -> dict[str, Any]:
    return _response(302, extra={"Location": APEX + path, "Cache-Control": "private, no-store, max-age=0"})


def _event_handler(event: Any, context: Any) -> dict[str, Any]:
    del context
    try:
        if isinstance(event, bytes):
            event = event.decode("utf-8")
        if isinstance(event, str):
            event = json.loads(event)
        if not isinstance(event, dict):
            raise ValueError("invalid event")
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError):
        return _response(400, b"Invalid request")

    http = (event.get("requestContext") or {}).get("http") or {}
    method = str(http.get("method") or event.get("httpMethod") or "").upper()
    if method not in {"GET", "HEAD"}:
        return _response(405, b"Method not allowed", extra={"Allow": "GET, HEAD"})
    head = method == "HEAD"
    raw_path = str(event.get("rawPath") or http.get("path") or event.get("path") or "")
    path = unquote(raw_path)
    if not path.startswith("/") or "\\" in path or "\x00" in path:
        return _response(400, b"Invalid path", head=head)

    host = str((event.get("headers") or {}).get("host") or "").split(":", 1)[0].lower()
    if path in {"/", "/index.html", "/en/", "/en/index.html"}:
        source_ip = str(http.get("sourceIp") or "")
        mainland = _is_mainland(source_ip)
        destination = ("/cn/" if mainland is not False else "/global/") if path.startswith("/index") or path == "/" else ("/en/cn/" if mainland is not False else "/global/")
        return _redirect(destination)

    # www is an alias only. Preserve explicit regional paths and do not let IP
    # geolocation override a visitor's deliberate /cn/ or /global/ URL.
    if host == "www.dailyalbumapp.com":
        return _redirect(path)

    relative = path.lstrip("/")
    if (SITE / relative).is_dir() and not path.endswith("/"):
        return _redirect(path + "/")
    if path.endswith("/"):
        relative += "index.html"
    candidate = (SITE / relative).resolve()
    if not candidate.is_relative_to(SITE.resolve()) or not candidate.is_file() or any(part.startswith(".") for part in Path(relative).parts):
        return _response(404, b"Not found", head=head)
    content_type = mimetypes.guess_type(candidate.name)[0] or "application/octet-stream"
    if content_type.startswith("text/") or content_type in {"application/javascript", "application/json"}:
        content_type += "; charset=utf-8"
    payload = candidate.read_bytes()
    cache = "public, max-age=300" if candidate.suffix == ".html" else "public, max-age=3600"
    return _response(200, payload, content_type=content_type,
                     extra={"Cache-Control": cache}, head=head)


def handler(event_or_environ: Any, context_or_start_response: Any) -> Any:
    """Accept both FC 2.0 WSGI HTTP calls and FC 3.0 event HTTP calls."""
    if not callable(context_or_start_response):
        return _event_handler(event_or_environ, context_or_start_response)

    environ = event_or_environ
    start_response = context_or_start_response
    request_uri = environ.get("fc.request_uri") or environ.get("PATH_INFO") or "/"
    path = urlsplit(request_uri).path or "/"
    event = {
        "rawPath": path,
        "headers": {"host": environ.get("HTTP_HOST", "")},
        "requestContext": {"http": {
            "method": environ.get("REQUEST_METHOD", ""),
            "path": path,
            "sourceIp": environ.get("REMOTE_ADDR", ""),
        }},
    }
    response = _event_handler(event, None)
    status = response["statusCode"]
    reason = {200: "OK", 302: "Found", 400: "Bad Request", 404: "Not Found", 405: "Method Not Allowed"}.get(status, "Unknown")
    headers = [(key, value) for key, value in response["headers"].items() if key.lower() != "content-length"]
    start_response(f"{status} {reason}", headers)
    if environ.get("REQUEST_METHOD", "").upper() == "HEAD":
        return [b""]
    body = response["body"]
    return [base64.b64decode(body) if response["isBase64Encoded"] else body.encode("utf-8")]
