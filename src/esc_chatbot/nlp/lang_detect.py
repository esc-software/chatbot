from langdetect import detect, DetectorFactory, LangDetectException

from ..config import settings

DetectorFactory.seed = 0

_SHORT_TEXT_THRESHOLD = 10


def detect_lang(text: str) -> str:
    if len(text) < _SHORT_TEXT_THRESHOLD:
        return settings.default_lang
    try:
        lang = detect(text)
        if lang in ("pt", "pt-br", "pt-pt"):
            return "pt"
        if lang == "en":
            return "en"
        return settings.default_lang
    except LangDetectException:
        return settings.default_lang
