import os

import uvicorn

from .config import settings


def main() -> None:
    workers_str = os.getenv("WEB_CONCURRENCY", "")
    workers = int(workers_str) if workers_str.isdigit() and int(workers_str) > 1 else 1

    uvicorn.run(
        "esc_chatbot.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
        workers=workers,
    )


if __name__ == "__main__":
    main()
