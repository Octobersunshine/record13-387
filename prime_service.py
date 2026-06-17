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


def _base_sieve(limit: int) -> list:
    is_prime = bytearray(b'\x01') * (limit + 1)
    is_prime[0:2] = b'\x00\x00'
    for i in range(2, int(math.isqrt(limit)) + 1):
        if is_prime[i]:
            is_prime[i * i::i] = b'\x00' * ((limit - i * i) // i + 1)
    return [i for i in range(2, limit + 1) if is_prime[i]]


def find_primes_in_range(a: int, b: int) -> list:
    if a > b or b < 2:
        return []
    start = max(2, a)
    sieve_size = b - start + 1
    sieve = bytearray(b'\x01') * sieve_size
    base_primes = _base_sieve(int(math.isqrt(b)))
    for p in base_primes:
        first = max(p * p, ((start + p - 1) // p) * p)
        if first % 2 == 0 and p != 2:
            first += p
        for j in range(first - start, sieve_size, p):
            sieve[j] = 0
    return [start + i for i in range(sieve_size) if sieve[i]]


def prime_pi(x: int) -> int:
    if x < 2:
        return 0
    is_prime = bytearray(b'\x01') * (x + 1)
    is_prime[0:2] = b'\x00\x00'
    for i in range(2, int(math.isqrt(x)) + 1):
        if is_prime[i]:
            is_prime[i * i::i] = b'\x00' * ((x - i * i) // i + 1)
    return sum(is_prime)


def next_prime(n: int) -> int:
    if n < 2:
        return 2
    candidate = n + 1
    if candidate % 2 == 0:
        candidate += 1 if candidate != 2 else 0
    while True:
        if is_prime(candidate):
            return candidate
        candidate += 2


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
        if parsed.path == "/pi":
            params = parse_qs(parsed.query)
            try:
                x = int(params.get("x", [])[0])
            except (IndexError, ValueError):
                self._send_json(400, {"error": "参数错误：请提供整数 x"})
                return
            if x < 0:
                self._send_json(400, {"error": "参数错误：x 必须是非负整数"})
                return
            result = prime_pi(x)
            self._send_json(200, {"x": x, "pi(x)": result})
            return
        if parsed.path == "/next_prime":
            params = parse_qs(parsed.query)
            try:
                n = int(params.get("n", [])[0])
            except (IndexError, ValueError):
                self._send_json(400, {"error": "参数错误：请提供整数 n"})
                return
            if n < 0:
                self._send_json(400, {"error": "参数错误：n 必须是非负整数"})
                return
            result = next_prime(n)
            self._send_json(200, {"n": n, "next_prime": result})
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
        if parsed.path == "/pi":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            try:
                data = json.loads(body)
                x = int(data["x"])
            except (json.JSONDecodeError, KeyError, ValueError, TypeError):
                self._send_json(400, {"error": "请求体错误：请提供 JSON 格式的 x"})
                return
            if x < 0:
                self._send_json(400, {"error": "参数错误：x 必须是非负整数"})
                return
            result = prime_pi(x)
            self._send_json(200, {"x": x, "pi(x)": result})
            return
        if parsed.path == "/next_prime":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            try:
                data = json.loads(body)
                n = int(data["n"])
            except (json.JSONDecodeError, KeyError, ValueError, TypeError):
                self._send_json(400, {"error": "请求体错误：请提供 JSON 格式的 n"})
                return
            if n < 0:
                self._send_json(400, {"error": "参数错误：n 必须是非负整数"})
                return
            result = next_prime(n)
            self._send_json(200, {"n": n, "next_prime": result})
            return
        self._send_json(404, {"error": "Not Found"})

    def log_message(self, format, *args):
        pass


def run_server(host: str = "127.0.0.1", port: int = 8000):
    server = HTTPServer((host, port), PrimeHandler)
    print(f"素数计算服务已启动：http://{host}:{port}")
    print(f"GET  /primes?a=<start>&b=<end>")
    print(f"POST /primes       JSON: {{\"a\": <start>, \"b\": <end>}}")
    print(f"GET  /pi?x=<n>           - 素数计数 π(x)")
    print(f"POST /pi           JSON: {{\"x\": <n>}}")
    print(f"GET  /next_prime?n=<k>   - 大于 k 的下一个素数")
    print(f"POST /next_prime  JSON: {{\"n\": <k>}}")
    print(f"GET  /health")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务已停止")
        server.server_close()


if __name__ == "__main__":
    run_server()
