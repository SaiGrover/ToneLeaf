import os
from pathlib import Path

from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles

from .engine import analyze
from .schemas import AnalysisRequest, AnalysisResponse

app = FastAPI(
    title="Toneleaf Local NLP",
    description="A local-memory-only sentiment and distress-language analysis service.",
    version="3.0.0",
    docs_url=None,
    redoc_url=None,
)
trusted_hosts = [host.strip() for host in os.getenv(
    "TONELEAF_TRUSTED_HOSTS", "127.0.0.1,localhost"
).split(",") if host.strip()]
app.add_middleware(TrustedHostMiddleware, allowed_hosts=trusted_hosts)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^http://(127\.0\.0\.1|localhost):\d{2,5}$",
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type"],
)


@app.middleware("http")
async def privacy_headers(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


@app.get("/health", include_in_schema=False)
def health(response: Response):
    response.headers["Cache-Control"] = "no-store"
    return {"status": "ok", "privacy": "local-memory-only"}


@app.post("/analyze", response_model=AnalysisResponse)
def run_analysis(payload: AnalysisRequest):
    # The request text is neither logged nor persisted; it becomes unreachable
    # after this synchronous analysis returns.
    return analyze(payload.text, payload.mode)


static_dir = Path(os.getenv("TONELEAF_STATIC_DIR", "")).resolve()
if os.getenv("TONELEAF_STATIC_DIR") and static_dir.is_dir():
    # Mounted last so API routes retain priority. In production FastAPI serves
    # the exported Next.js interface and API from one privacy-controlled origin.
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="web")
