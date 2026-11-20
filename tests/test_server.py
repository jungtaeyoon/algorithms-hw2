import http.client
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.parse import urlencode

from src import server
from src.shortener import URLShortener


class ServerTest(unittest.TestCase):
    def setUp(self):
        server.shortener = URLShortener(table_type="chaining")
        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.ShortenerHandler)
        self.port = self.httpd.server_address[1]
        self.thread = threading.Thread(target=self.httpd.serve_forever)
        self.thread.start()

    def tearDown(self):
        self.httpd.shutdown()
        self.thread.join()
        self.httpd.server_close()

    def request(self, method, path, body=None, headers=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.port)
        connection.request(method, path, body=body, headers=headers or {})
        response = connection.getresponse()
        data = response.read().decode("utf-8")
        result = (response.status, response.getheader("Location"), data)
        connection.close()
        return result

    def test_form_post_redirect_and_missing_code(self):
        status, _, body = self.request("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn('action="/shorten"', body)
        self.assertIn('name="url"', body)
        self.assertIn('href="/table"', body)

        form = urlencode({"url": "https://example.com/article"}).encode("ascii")
        status, _, body = self.request(
            "POST",
            "/shorten",
            form,
            {"Content-Type": "application/x-www-form-urlencoded"},
        )
        self.assertEqual(status, 200)
        self.assertIn('href="/1"', body)
        self.assertIn("https://example.com/article", body)

        status, location, _ = self.request("GET", "/1")
        self.assertEqual(status, 302)
        self.assertEqual(location, "https://example.com/article")

        status, _, _ = self.request("GET", "/missing")
        self.assertEqual(status, 404)

    def test_table_shows_chain_arrow_and_horner_details(self):
        form = urlencode({"url": "https://example.com/table"}).encode("ascii")
        self.request(
            "POST",
            "/shorten",
            form,
            {"Content-Type": "application/x-www-form-urlencoded"},
        )
        status, _, body = self.request("GET", "/table")
        self.assertEqual(status, 200)
        self.assertIn("https://example.com/table", body)
        self.assertIn("Short code: 1", body)
        self.assertIn("Short link:", body)
        self.assertIn("&rarr;", body)
        self.assertIn("<details>", body)
        self.assertIn("Horner", body)


if __name__ == "__main__":
    unittest.main()
