import json
import time
from pathlib import Path

from ..config import settings


class ChatLogger:
    def __init__(self) -> None:
        self._path = Path(settings.log_file)
        self._path.parent.mkdir(parents=True, exist_ok=True)

    def _write(self, level: str, data: dict) -> None:
        entry = {"level": level, "ts": time.time(), **data}
        with open(str(self._path), "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def info(self, user: str, text: str, intent: str, score: float) -> None:
        self._write("INFO", {"user": user, "text": text, "intent": intent, "score": score})

    def warn(self, user: str, text: str, reason: str) -> None:
        self._write("WARN", {"user": user, "text": text, "reason": reason})

    def error(self, user: str, text: str, error: str) -> None:
        self._write("ERROR", {"user": user, "text": text, "error": error})


logger = ChatLogger()
