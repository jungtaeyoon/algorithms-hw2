import http.client
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.parse import urlencode

from src import server
from src.hash_table import HashTable, LinearHashTable
from src.shortener import URLShortener


class ServerTest(unittest.TestCase):
    def setUp(self):
        server.table_kind = "chaining"
        server.chaining_table = HashTable()
        server.linear_table = LinearHashTable()
        server.shortener = URLShortener(table=server.chaining_table)
        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.ShortenerHandler)
        self.port = self.httpd.server_address[1]
        self.thread = threading.Thread(target=self.httpd.serve_forever)
        self.thread.start()

    def tearDown(self):
        self.httpd.shutdown()
        self.thread.join()
        self.httpd.server_close()

    def request(self, method, path, body=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.port)
        headers = {}
        if body is not None:
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        connection.request(method, path, body=body, headers=headers)
        response = connection.getresponse()
        data = response.read().decode("utf-8")
        result = response.status, response.getheader("Location"), data
        connection.close()
        return result

    def test_form_redirect_and_both_tables(self):
        status, _, form = self.request("GET", "/")
        self.assertEqual(status, 200)
        self.assertIn('action="/shorten"', form)

        body = urlencode({"url": "https://example.com/issue8"}).encode("ascii")
        status, _, result = self.request("POST", "/shorten", body)
        self.assertEqual(status, 200)
        self.assertIn('href="/1"', result)

        status, location, _ = self.request("GET", "/1")
        self.assertEqual(status, 302)
        self.assertEqual(location, "https://example.com/issue8")

        status, _, table = self.request("GET", "/table")
        self.assertEqual(status, 200)
        self.assertIn("개별 체이닝", table)
        self.assertIn("선형 탐지", table)
        self.assertIn("Horner hash 및 충돌 과정", table)
        self.assertIn("충돌 시 다음 칸으로 순차 이동", table)

    def test_linear_table_shortens_and_redirects(self):
        server.table_kind = "linear"
        server.linear_table = LinearHashTable()
        server.shortener = URLShortener(table=server.linear_table)

        body = urlencode({"url": "https://example.com/linear"}).encode("ascii")
        status, _, result = self.request("POST", "/shorten", body)
        self.assertEqual(status, 200)
        self.assertIn('href="/1"', result)

        status, location, _ = self.request("GET", "/1")
        self.assertEqual(status, 302)
        self.assertEqual(location, "https://example.com/linear")

        status, _, table = self.request("GET", "/table")
        self.assertEqual(status, 200)
        self.assertIn("선형 탐지", table)
        self.assertIn("Short code: 1", table)


if __name__ == "__main__":
    unittest.main()
