"""Small HTTP server for the URL shortener."""

import argparse
import html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

try:
    from .hash_table import HashTable, LinearHashTable, horner_hash
    from .shortener import URLShortener, validate_url
except ImportError:
    from hash_table import HashTable, LinearHashTable, horner_hash
    from shortener import URLShortener, validate_url


table_kind = "chaining"
chaining_table = HashTable()
linear_table = LinearHashTable()
shortener = URLShortener(table=chaining_table)


FORM = """<!doctype html>
<html><head><meta charset="utf-8"><title>URL Shortener</title></head>
<body><h1>URL Shortener</h1>
<p><a href="/table">개별 체이닝과 선형 탐지 테이블 보기</a></p>
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
        if table_kind == "chaining":
            linear_table.put(code, url)
        else:
            chaining_table.put(code, url)
        body = (
            "<h1>Short URL</h1>"
            f'<p><a href="/{html.escape(code)}">/{html.escape(code)}</a></p>'
            f"<p>원본: {html.escape(url)}</p>"
        )
        self.send_html(200, body)

    def send_table(self):
        chaining_rows = self.format_chaining_table(chaining_table)
        linear_rows = self.format_linear_table(linear_table)
        body = (
            "<!doctype html><html><head><meta charset=\"utf-8\">"
            "<title>Hash Table Comparison</title>"
            "<style>body{font-family:sans-serif;max-width:960px;margin:2rem auto}"
            ".slot{margin:.75rem;padding:.75rem;border:1px solid #bbb}"
            ".node{display:inline-block;margin:.25rem;padding:.5rem;border:1px solid #333}"
            ".arrow{margin:0 .25rem;font-weight:bold}</style></head><body>"
            "<h1>Hash Table Comparison</h1>"
            "<p><a href=\"/\">URL 단축 폼으로 돌아가기</a></p>"
            "<h2>개별 체이닝 (Separate Chaining)</h2>"
            + chaining_rows
            + "<h2>선형 탐지 (Linear Probing)</h2>"
            + linear_rows
            + "</body></html>"
        )
        self.send_html(200, body)

    def format_chaining_table(self, table):
        rows = []
        for index, bucket in enumerate(table.table):
            chain = []
            node = bucket
            while node is not None:
                chain.append(self.format_node(node.key, node.value, table.size, "chain"))
                node = node.next
            details = "".join(
                node_html
                + ("<span class=\"arrow\">&rarr;</span>" if position < len(chain) - 1 else "")
                for position, node_html in enumerate(chain)
            ) if chain else "empty"
            if chain:
                details += "<span class=\"arrow\">&rarr;</span><span class=\"node\">null</span>"
            rows.append(
                f"<div class=\"slot\"><strong>칸 {index}</strong><div>{details}</div></div>"
            )
        return "".join(rows)

    def format_linear_table(self, table):
        rows = []
        for index, key in enumerate(table.keys):
            if key is table._EMPTY:
                details = "empty"
            elif key is table._TOMB:
                details = "deleted (tombstone)"
            else:
                details = self.format_node(key, table.values[index], table.size, "linear")
            rows.append(
                f"<div class=\"slot\"><strong>칸 {index}</strong><div>{details}</div></div>"
            )
        return "".join(rows)

    def format_node(self, code, url, table_size, mode):
        escaped_code = html.escape(str(code))
        escaped_url = html.escape(str(url))
        index = horner_hash(str(code), table_size)
        value = 0
        steps = []
        for char in str(code):
            before = value
            value = (value * 31 + ord(char)) % table_size
            steps.append(
                f"{before} * 31 + ord('{html.escape(char)}')={before * 31 + ord(char)}, "
                f"mod {table_size} = {value}"
            )
        process = (
            "충돌 시 다음 칸으로 순차 이동" if mode == "linear"
            else "충돌 시 같은 칸의 연결 리스트 앞에 노드 추가"
        )
        return (
            "<span class=\"node\">"
            f"URL key: {escaped_url}<br>"
            f"Short code: {escaped_code}<br>"
            f'Short link: <a href="/{escaped_code}">/{escaped_code}</a>'
            "<details><summary>Horner hash 및 충돌 과정</summary>"
            + "<br>".join(steps)
            + f"<br>최종 호너 인덱스: {index}<br>{process}"
            + "</details></span>"
        )

    def log_message(self, format, *args):
        return


def serve(port=8000):
    server = ThreadingHTTPServer(("0.0.0.0", port), ShortenerHandler)
    print(f"Serving on port {port}")
    server.serve_forever()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--table", choices=("chaining", "linear"), default="chaining")
    args = parser.parse_args()
    global table_kind, shortener, chaining_table, linear_table
    table_kind = args.table
    chaining_table = HashTable()
    linear_table = LinearHashTable()
    if table_kind == "linear":
        shortener = URLShortener(table=linear_table)
    else:
        shortener = URLShortener(table=chaining_table)
    serve(args.port)


if __name__ == "__main__":
    main()
