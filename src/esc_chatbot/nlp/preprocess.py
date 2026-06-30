import re

from deep_translator import GoogleTranslator

from ..config import settings
from .lang_detect import detect_lang
from .spell import correct


_PATTERNS_BLACKLIST = [
    re.compile(p, re.IGNORECASE)
    for p in [
        r"ignore previous instructions",
        r"system prompt",
        r"act as",
        r"you are now",
        r"<script.*?>",
        r"drop table",
        r"select .* from",
        r"--",
        r";--",
    ]
]
_RE_NON_ALPHA = re.compile(r"[^a-zà-ú0-9\s]")
_RE_WHITESPACE = re.compile(r"\s+")
_RE_REPEATED_CHAR = re.compile(r"(.)\1{6,}")

_TRANSLATORS: dict[tuple[str, str], GoogleTranslator] = {}


def _get_translator(source: str, target: str) -> GoogleTranslator:
    key = (source, target)
    t = _TRANSLATORS.get(key)
    if t is None:
        t = GoogleTranslator(source=source, target=target)
        _TRANSLATORS[key] = t
    return t


def to_base_language(text: str) -> tuple[str, str]:
    if not settings.enable_translation:
        return text, detect_lang(text)

    lang = detect_lang(text)
    if lang != settings.default_lang:
        try:
            t = _get_translator(lang, settings.default_lang)
            translated = t.translate(text)
            return translated, lang
        except Exception:
            pass
    return text, lang


def from_base_language(text: str, target_lang: str) -> str:
    if not settings.enable_translation:
        return text
    if target_lang != settings.default_lang:
        try:
            t = _get_translator(settings.default_lang, target_lang)
            return t.translate(text)
        except Exception:
            pass
    return text


def clean(text: str) -> str:
    lowered = text.lower()
    for p in _PATTERNS_BLACKLIST:
        lowered = p.sub(" ", lowered)
    lowered = _RE_NON_ALPHA.sub(" ", lowered)
    lowered = _RE_WHITESPACE.sub(" ", lowered).strip()
    if _RE_REPEATED_CHAR.search(lowered):
        return ""
    lowered = lowered[:300]

    if settings.spell_enabled:
        lowered = correct(lowered)

    return lowered
