import json
import threading
import unittest
from http.server import HTTPServer
from urllib.request import Request, urlopen

from api.analyze import handler as AnalyzeHandler
from api.health import handler as HealthHandler


def request(handler_class, path="/", payload=None):
    server = HTTPServer(("127.0.0.1", 0), handler_class)
    thread = threading.Thread(target=server.handle_request, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{server.server_port}{path}"
    if payload is None:
        response = urlopen(url, timeout=3)
    else:
        body = json.dumps(payload).encode()
        response = urlopen(
            Request(url, data=body, headers={"Content-Type": "application/json"}),
            timeout=3,
        )
    result = response.status, response.headers, json.loads(response.read())
    thread.join(timeout=3)
    server.server_close()
    return result


class VercelHandlerTests(unittest.TestCase):
    def test_health_handler(self):
        status, headers, body = request(HealthHandler, "/api/health")
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "ok")
        self.assertEqual(headers["Cache-Control"], "no-store")

    def test_analysis_handler(self):
        status, headers, body = request(
            AnalyzeHandler,
            "/api/analyze",
            {"text": "You are disgusting.", "mode": "polarity"},
        )
        self.assertEqual(status, 200)
        self.assertEqual(body["label"], "negative")
        self.assertEqual(body["privacy"], "hosted-memory-only")
        self.assertEqual(headers["Cache-Control"], "no-store")


if __name__ == "__main__":
    unittest.main()
