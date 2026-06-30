import time

from ..config import settings
from ..core.log import logger
from ..core.security import detect_injection
from ..nlp import INTENTS
from ..nlp.preprocess import clean, from_base_language, to_base_language
from ..nlp.ner import extract_entities
from ..nlp.sentiment import analyze_sentiment


def validate_input(text: str | None) -> tuple[bool, str]:
    if text is None:
        return False, "empty"
    if not isinstance(text, str):
        return False, "invalid_type"
    text = text.strip()
    if len(text) < 2:
        return False, "too_short"
    if len(text) > 300:
        return False, "too_long"
    return True, text


def safe_translate(text: str, detected_lang: str) -> str:
    if not settings.enable_translation:
        return text
    try:
        return from_base_language(text, detected_lang)
    except Exception:
        return text


def get_response(engine, intent: str, lang: str = "pt") -> str:
    for i in INTENTS["intents"]:
        if i["tag"] != intent:
            continue
        responses = i.get("responses", {})
        if isinstance(responses, dict):
            candidates = responses.get(lang) or responses.get("pt", [])
        else:
            candidates = responses
        if not candidates:
            break
        return engine.get_diverse_response(intent, candidates)
    return safe_translate("I didn't understand.", lang)


def process_chat(params: dict, ip: str, engine, memory, feedback_sys) -> dict:
    raw_text = params["text"]

    if detect_injection(raw_text):
        logger.warn(ip, raw_text, "blocked_injection")
        return {"response": "Request not allowed.", "blocked": True}

    try:
        text_base, detected_lang = to_base_language(raw_text)
    except Exception:
        logger.error(ip, raw_text, "translation_failed")
        text_base, detected_lang = raw_text, settings.default_lang

    text = clean(text_base)
    if not text:
        logger.warn(ip, raw_text, "empty_after_clean")
        return {"response": "Message could not be processed."}

    ctx = [m["text"] for m in memory.get(ip)]
    intent, base_score = engine.retrieve(text, context=ctx, pre_cleaned=True)
    score = feedback_sys.adjusted_confidence(intent, base_score)
    entities = extract_entities(text)

    sentiment = None
    if settings.sentiment_enabled:
        sentiment = analyze_sentiment(text)

    memory.append(ip, {"text": text, "intent": intent, "lang": detected_lang})
    logger.info(ip, text, intent, score)

    response = get_response(engine, intent, detected_lang)

    return {
        "intent": intent,
        "response": response,
        "entities": entities,
        "score": score,
        "memory": memory.get(ip),
        "lang": detected_lang,
        "sentiment": sentiment,
    }
