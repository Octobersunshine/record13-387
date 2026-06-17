import math
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(math.isqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True


def find_primes_in_range(a: int, b: int) -> list:
    if a > b:
        return []
    start = max(2, a)
    primes = []
    sieve = [True] * (b - start + 1)
    limit = int(math.isqrt(b))
    for i in range(2, limit + 1):
        first = max(i * i, ((start + i - 1) // i) * i)
        for j in range(first, b + 1, i):
            if j >= start:
                sieve[j - start] = False
    for idx, is_p in enumerate(sieve):
        if is_p:
            primes.append(start + idx)
    return primes


class PrimeHandler(BaseHTTPRequestHandler):
    def _send_json(self, status_code: int, data: dict):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/primes":
            params = parse_qs(parsed.query)
            try:
                a = int(params.get("a", [])[0])
                b = int(params.get("b", [])[0])
            except (IndexError, ValueError):
                self._send_json(400, {"error": "参数错误：请提供整数 a 和 b"})
                return
            if a < 0 or b < 0:
                self._send_json(400, {"error": "参数错误：a 和 b 必须是非负整数"})
                return
            primes = find_primes_in_range(a, b)
            self._send_json(200, {
                "range": [a, b],
                "count": len(primes),
                "primes": primes
            })
            return
        if parsed.path == "/health":
            self._send_json(200, {"status": "ok"})
            return
        self._send_json(404, {"error": "Not Found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/primes":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            try:
                data = json.loads(body)
                a = int(data["a"])
                b = int(data["b"])
            except (json.JSONDecodeError, KeyError, ValueError, TypeError):
                self._send_json(400, {"error": "请求体错误：请提供 JSON 格式的 a 和 b"})
                return
            if a < 0 or b < 0:
                self._send_json(400, {"error": "参数错误：a 和 b 必须是非负整数"})
                return
            primes = find_primes_in_range(a, b)
            self._send_json(200, {
                "range": [a, b],
                "count": len(primes),
                "primes": primes
            })
            return
        self._send_json(404, {"error": "Not Found"})

    def log_message(self, format, *args):
        pass


def run_server(host: str = "127.0.0.1", port: int = 8000):
    server = HTTPServer((host, port), PrimeHandler)
    print(f"素数计算服务已启动：http://{host}:{port}")
    print(f"GET  /primes?a=<start>&b=<end>")
    print(f"POST /primes  JSON: {{\"a\": <start>, \"b\": <end>}}")
    print(f"GET  /health")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务已停止")
        server.server_close()


if __name__ == "__main__":
    run_server()
