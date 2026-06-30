import json
import time
from collections import deque
from pathlib import Path

from ..config import settings


try:
    import redis as _redis

    _redis_client: _redis.Redis | None = _redis.Redis.from_url(
        settings.redis_url, decode_responses=True
    ) if settings.redis_url else None
    _redis_client.ping() if _redis_client else None
except Exception:
    _redis_client = None


def _r() -> bool:
    return _redis_client is not None


class MemoryBackend:
    _SAVE_INTERVAL = 10

    def __init__(self) -> None:
        self.maxlen = settings.memory_maxlen
        if _r():
            return
        self._data: dict[str, deque] = {}
        self._file = Path(settings.memory_file)
        self._ops_since_save = 0
        self._load_file()

    def append(self, key: str, entry: dict) -> None:
        if _r():
            _redis_client.lpush(f"mem:{key}", json.dumps(entry, ensure_ascii=False))
            _redis_client.ltrim(f"mem:{key}", 0, self.maxlen - 1)
            return
        if key not in self._data:
            self._data[key] = deque(maxlen=self.maxlen)
        self._data[key].append(entry)
        self._ops_since_save += 1
        if self._ops_since_save >= self._SAVE_INTERVAL:
            self.save()
            self._ops_since_save = 0

    def get(self, key: str) -> list[dict]:
        if _r():
            raw = _redis_client.lrange(f"mem:{key}", 0, -1)
            return [json.loads(r) for r in reversed(raw)]
        return list(self._data.get(key, []))

    def clear(self, key: str) -> None:
        if _r():
            _redis_client.delete(f"mem:{key}")
            return
        self._data.pop(key, None)
        if not _r():
            self.save()

    def count_users(self) -> int:
        if _r():
            keys = _redis_client.keys("mem:*")
            return len(keys)
        return len(self._data)

    def save(self) -> None:
        if _r():
            return
        self._file.parent.mkdir(parents=True, exist_ok=True)
        serializable = {k: list(v) for k, v in self._data.items()}
        with open(str(self._file), "w") as f:
            json.dump(serializable, f)

    def _load_file(self) -> None:
        if not self._file.exists():
            return
        try:
            with open(str(self._file)) as f:
                data = json.load(f)
            for k, v in data.items():
                self._data[k] = deque(v, maxlen=self.maxlen)
        except (json.JSONDecodeError, OSError):
            pass


class FeedbackBackend:
    def __init__(self) -> None:
        self._file = Path(settings.feedback_file)
        self._file.parent.mkdir(parents=True, exist_ok=True)
        self._score_map: dict[str, list[int]] = {}
        if _r():
            return
        self._load_file()

    def record(self, user: str, text: str, intent: str, positive: bool, comment: str = "") -> None:
        entry = {
            "user": user,
            "text": text,
            "intent": intent,
            "positive": positive,
            "comment": comment,
            "ts": time.time(),
        }
        raw = json.dumps(entry, ensure_ascii=False)
        if _r():
            _redis_client.rpush("feedback", raw)
        else:
            with open(str(self._file), "a") as f:
                f.write(raw + "\n")

        self._score_map.setdefault(intent, []).append(1 if positive else -1)

    def adjusted_confidence(self, intent: str, base: float) -> float:
        scores = self._score_map.get(intent, [])
        if not scores:
            return base
        avg = sum(scores) / len(scores)
        adjustment = avg * 0.1
        return max(0.1, min(1.0, base + adjustment))

    def total_count(self) -> int:
        if _r():
            return _redis_client.llen("feedback")
        if not self._file.exists():
            return 0
        try:
            with open(str(self._file)) as f:
                return sum(1 for _ in f if _.strip())
        except OSError:
            return 0

    def intent_stats(self, intent: str) -> dict:
        scores = self._score_map.get(intent, [])
        total = len(scores)
        positives = sum(1 for s in scores if s > 0)
        return {
            "total": total,
            "positive": positives,
            "negative": total - positives,
            "score": sum(scores) if scores else 0,
        }

    def _load_file(self) -> None:
        if not self._file.exists():
            return
        try:
            with open(str(self._file)) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    entry = json.loads(line)
                    self._score_map.setdefault(entry["intent"], []).append(
                        1 if entry["positive"] else -1
                    )
        except (json.JSONDecodeError, OSError):
            pass
