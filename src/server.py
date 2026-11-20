"""Small HTTP server for the URL shortener."""

import argparse
import html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

try:
    from .hash_table import HashTable
    from .shortener import URLShortener, validate_url
except ImportError:
    from hash_table import HashTable
    from shortener import URLShortener, validate_url


shortener = URLShortener(table=HashTable())


FORM = """<!doctype html>
<html><head><meta charset="utf-8"><title>URL Shortener</title></head>
<body><h1>URL Shortener</h1>
<form method="post" action="/shorten">
<label>URL <input name="url" type="url" size="60" required></label>
<button type="submit">Shorten</button>
</form></body></html>"""


class ShortenerHandler(BaseHTTPRequestHandler):
    def send_html(self, status, body):
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            self.send_html(200, FORM)
        elif path == "/table":
            self.send_table()
        elif path.startswith("/"):
            code = path[1:]
            if "/" not in code:
                try:
                    url = shortener.expand(code)
                except (KeyError, ValueError, TypeError):
                    self.send_html(404, "<h1>404 Not Found</h1>")
                else:
                    self.send_response(302)
                    self.send_header("Location", url)
                    self.end_headers()
            else:
                self.send_html(404, "<h1>404 Not Found</h1>")
        else:
            self.send_html(404, "<h1>404 Not Found</h1>")

    def do_POST(self):
        path = urlparse(self.path).path
        if path != "/shorten":
            self.send_html(404, "<h1>404 Not Found</h1>")
            return
        length = int(self.headers.get("Content-Length", "0"))
        fields = parse_qs(self.rfile.read(length).decode("utf-8"))
        url = fields.get("url", [""])[0]
        try:
            validate_url(url)
            code = shortener.shorten(url)
        except (TypeError, ValueError):
            self.send_html(400, "<h1>잘못된 URL</h1><p>http:// 또는 https://로 시작하는 주소를 입력하세요.</p>")
            return
        body = (
            "<h1>Short URL</h1>"
            f'<p><a href="/{html.escape(code)}">/{html.escape(code)}</a></p>'
            f"<p>원본: {html.escape(url)}</p>"
        )
        self.send_html(200, body)

    def send_table(self):
        table = shortener.code_to_url
        rows = []
        for index, bucket in enumerate(table.table):
            node = bucket
            chain = []
            while node is not None:
                chain.append(f"{html.escape(node.key)} -> {html.escape(str(node.value))}")
                node = node.next
            details = ", ".join(chain) if chain else "empty"
            rows.append(
                f"<tr><td>{index}</td><td>{details}</td>"
                f"<td>Horner hash of code mod {table.size}</td></tr>"
            )
        body = (
            "<h1>Hash Table</h1><table border='1'><tr><th>Slot</th><th>Chain</th><th>Calculation</th></tr>"
            + "".join(rows)
            + "</table>"
        )
        self.send_html(200, body)

    def log_message(self, format, *args):
        return


def serve(port=8000):
    server = ThreadingHTTPServer(("0.0.0.0", port), ShortenerHandler)
    print(f"Serving on port {port}")
    server.serve_forever()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    serve(args.port)


if __name__ == "__main__":
    main()
