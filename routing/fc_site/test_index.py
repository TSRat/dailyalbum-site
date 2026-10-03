"""Exercise the packaged FC entry point with actual candidate site files."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from build_package import OUTPUT, main as build_package


class SiteHandlerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        build_package()
        cls.temp = tempfile.TemporaryDirectory()
        with ZipFile(OUTPUT) as archive:
            archive.extractall(cls.temp.name)
        spec = importlib.util.spec_from_file_location("fc_site_test", Path(cls.temp.name) / "index.py")
        cls.module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(cls.module)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def request(self, path: str, ip: str = "114.114.114.114", *, host: str = "dailyalbumapp.com", method: str = "GET") -> dict:
        event = {
            "rawPath": path,
            "headers": {"host": host, "x-forwarded-for": "8.8.8.8"},
            "requestContext": {"http": {"method": method, "sourceIp": ip}},
        }
        return self.module.handler(event, None)

    def test_root_uses_gateway_ip_not_untrusted_forwarded_header(self) -> None:
        self.assertEqual(self.request("/")["headers"]["Location"], "https://dailyalbumapp.com/cn/")
        self.assertEqual(self.request("/", "8.8.8.8")["headers"]["Location"], "https://dailyalbumapp.com/global/")
        self.assertEqual(self.request("/", "2400:3200::1")["headers"]["Location"], "https://dailyalbumapp.com/cn/")
        self.assertEqual(self.request("/", "2001:4860:4860::8888")["headers"]["Location"], "https://dailyalbumapp.com/global/")

    def test_explicit_edition_is_stable_across_ips(self) -> None:
        for ip in ("114.114.114.114", "8.8.8.8"):
            self.assertEqual(self.request("/cn/", ip)["statusCode"], 200)
            self.assertEqual(self.request("/global/", ip)["statusCode"], 200)

    def test_www_preserves_explicit_path(self) -> None:
        result = self.request("/global/privacy/", host="www.dailyalbumapp.com")
        self.assertEqual(result["headers"]["Location"], "https://dailyalbumapp.com/global/privacy/")

    def test_static_asset_and_head(self) -> None:
        self.assertEqual(self.request("/styles.css")["statusCode"], 200)
        icon = self.request("/app-icon.png")
        self.assertEqual(icon["statusCode"], 200)
        self.assertTrue(icon["isBase64Encoded"])
        head = self.request("/app-icon.png", method="HEAD")
        self.assertEqual(head["body"], "")
        self.assertEqual(head["headers"]["Content-Length"], icon["headers"]["Content-Length"])

    def test_path_escape_and_method_are_rejected(self) -> None:
        self.assertEqual(self.request("/%2e%2e/CNAME")["statusCode"], 404)
        self.assertEqual(self.request("/cn/", method="POST")["statusCode"], 405)

    def test_fc_2_wsgi_http_entry(self) -> None:
        captured = []

        def start_response(status, headers):
            captured.append((status, dict(headers)))

        environ = {"REQUEST_METHOD": "GET", "REMOTE_ADDR": "8.8.8.8", "HTTP_HOST": "dailyalbumapp.com", "fc.request_uri": "/?from=home"}
        body = b"".join(self.module.handler(environ, start_response))
        self.assertEqual(body, b"")
        self.assertEqual(captured[0][0], "302 Found")
        self.assertEqual(captured[0][1]["Location"], "https://dailyalbumapp.com/global/")

        environ.update({"REQUEST_METHOD": "HEAD", "fc.request_uri": "/cn/privacy/"})
        body = b"".join(self.module.handler(environ, start_response))
        self.assertEqual(body, b"")
        self.assertEqual(captured[1][0], "200 OK")


if __name__ == "__main__":
    unittest.main()
