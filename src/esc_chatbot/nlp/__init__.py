from .intents import INTENTS
from .ner import extract_entities
from .preprocess import clean, from_base_language, to_base_language
from .sentiment import analyze_sentiment


def NLPAttention(*args, **kwargs):
    from .engine import NLPAttention as _NLPAttention
    return _NLPAttention(*args, **kwargs)


__all__ = [
    "NLPAttention",
    "INTENTS",
    "clean",
    "to_base_language",
    "from_base_language",
    "extract_entities",
    "analyze_sentiment",
]
