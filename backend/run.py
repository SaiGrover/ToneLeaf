import os

import uvicorn


if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host=os.getenv("TONELEAF_HOST", "127.0.0.1"),
        port=int(os.getenv("TONELEAF_PORT", os.getenv("PORT", "8765"))),
        access_log=False,
        log_level="warning",
    )
