"""Stateless Vercel sentiment-analysis function for Toneleaf."""

import json
from http.server import BaseHTTPRequestHandler

from backend.engine import analyze


MAX_BODY_BYTES = 24_000


class handler(BaseHTTPRequestHandler):
    def _json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Pragma", "no-cache")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._json(400, {"detail": "Invalid content length"})
            return
        if length <= 0 or length > MAX_BODY_BYTES:
            self._json(413, {"detail": "Request body is empty or too large"})
            return
        try:
            payload = json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._json(400, {"detail": "Invalid JSON"})
            return

        text = payload.get("text") if isinstance(payload, dict) else None
        mode = payload.get("mode", "polarity") if isinstance(payload, dict) else None
        if not isinstance(text, str) or not text.strip() or len(text) > 5_000:
            self._json(422, {"detail": "Text must contain 1 to 5,000 characters"})
            return
        if mode not in {"polarity", "distress"}:
            self._json(422, {"detail": "Mode must be polarity or distress"})
            return

        result = analyze(text.strip(), mode)
        result["privacy"] = "hosted-memory-only"
        self._json(200, result)

    def log_message(self, format: str, *args) -> None:
        # Avoid application-level request logging; Vercel infrastructure may
        # still retain platform metadata according to the project settings.
        return
