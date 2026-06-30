import re

from ..config import settings


_RE_EMAIL = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
_RE_PHONE = re.compile(r"(?:\+\d{1,3}\s?)?\(?\d{2,3}\)?\s?\d{4,5}-?\d{4}")
_RE_URL = re.compile(r"https?://[^\s]+")
_RE_MONEY = re.compile(r"r?\$\s?\d+(?:[.,]\d+)?|\d+\s?(?:reais|dólares|euros)")
_RE_NUMBER = re.compile(r"\d+")
_RE_COMPANY = re.compile(
    r"(?:@|da\s|do\s|na\s|no\s)?([A-Z][a-z]+(?:[-\s][A-Z][a-z]+)+)"
)


def extract_entities(text: str) -> dict[str, list[str]]:
    entities: dict[str, list[str]] = {}

    if settings.ner_enable_emails:
        emails = _RE_EMAIL.findall(text)
        if emails:
            entities["emails"] = emails

    if settings.ner_enable_phones:
        phones = _RE_PHONE.findall(text)
        if phones:
            entities["phones"] = phones

    if settings.ner_enable_urls:
        urls = _RE_URL.findall(text)
        if urls:
            entities["urls"] = urls

    if settings.ner_enable_money:
        money = _RE_MONEY.findall(text.lower())
        if money:
            entities["money"] = money

    numbers = _RE_NUMBER.findall(text)
    if numbers:
        entities["numbers"] = numbers

    companies = _RE_COMPANY.findall(text)
    if companies:
        entities["companies"] = companies

    return entities
