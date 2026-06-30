import json
from collections import Counter
from pathlib import Path

from ..config import settings
from ..core.log import logger
from ..nlp import INTENTS


def train(engine, ip: str) -> dict:
    positive_feedbacks = []
    log_path = Path(settings.log_file)
    if log_path.exists():
        try:
            with open(str(log_path)) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    entry = json.loads(line)
                    if entry.get("level") == "INFO" and "feedback_" in entry.get("intent", ""):
                        positive_feedbacks.append(entry["text"])
        except (json.JSONDecodeError, OSError):
            pass

    faq_path = Path(settings.faq_file)
    if faq_path.exists():
        try:
            with open(str(faq_path)) as f:
                faq_data = json.load(f)
                for item in faq_data:
                    positive_feedbacks.append(item.get("question", ""))
        except (json.JSONDecodeError, OSError):
            pass

    if positive_feedbacks:
        new_patterns = list(set(positive_feedbacks[:20]))
        fallback = None
        for intent in INTENTS["intents"]:
            if intent["tag"] == "fallback":
                fallback = intent
        if fallback is None:
            INTENTS["intents"].append(
                {"tag": "faq_auto", "patterns": [], "responses": ["Thanks for your feedback!"]}
            )
            fallback = INTENTS["intents"][-1]
        existing = set(fallback.get("patterns", []))
        for p in new_patterns:
            if p not in existing:
                fallback.setdefault("patterns", []).append(p)
                existing.add(p)

    engine.retrain()
    logger.info(ip, "autotrain", "admin_train", 1.0)
    return {
        "status": "ok",
        "patterns_added": len(positive_feedbacks[:20]) if positive_feedbacks else 0,
    }


def extract_faq(engine, ip: str) -> dict:
    log_path = Path(settings.log_file)
    questions: list[str] = []
    if log_path.exists():
        try:
            with open(str(log_path)) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    entry = json.loads(line)
                    if entry.get("level") == "INFO" and entry.get("intent") == "fallback":
                        continue
                    if entry.get("level") == "INFO" and entry.get("text"):
                        questions.append(entry["text"])
        except (json.JSONDecodeError, OSError):
            pass

    counter = Counter(questions)
    top = counter.most_common(20)

    def _get_response(intent: str) -> str:
        for i in INTENTS["intents"]:
            if i["tag"] != intent:
                continue
            candidates = i.get("responses", {})
            if isinstance(candidates, dict):
                candidates = candidates.get("pt", [])
            if candidates:
                import random
                return random.choice(candidates)
        return ""

    faq = []
    for q, count in top:
        intent, score = engine.retrieve(q)
        response = _get_response(intent)
        faq.append({
            "question": q,
            "frequency": count,
            "matched_intent": intent,
            "suggested_response": response,
        })

    faq_path = Path(settings.faq_file)
    try:
        faq_path.parent.mkdir(parents=True, exist_ok=True)
        with open(str(faq_path), "w") as f:
            json.dump(faq, f, ensure_ascii=False, indent=2)
    except OSError:
        pass

    logger.info(ip, "faq_extraction", "admin_faq", 1.0)
    return {"status": "ok", "faq": faq}
