import re

POSITIVE_WORDS: set[str] = {
    "bom", "ótimo", "excelente", "maravilhoso", "perfeito", "legal",
    "show", "top", "incrível", "adoro", "amo", "gostei", "obrigado",
    "obrigada", "valeu", "nice", "great", "awesome", "perfect",
    "excellent", "love", "thanks", "good", "best", "helpful",
}

NEGATIVE_WORDS: set[str] = {
    "ruim", "péssimo", "horrível", "terrível", "odeio", "detesto",
    "pior", "fraca", "lento", "demorado", "problema", "erro",
    "bug", "falhou", "parou", "travou", "bad", "terrible",
    "horrible", "hate", "worst", "slow", "broken", "error",
    "fail", "frustrado", "chateado",
}


def analyze_sentiment(text: str) -> dict:
    words = set(re.findall(r"[a-zà-ú]+", text.lower()))
    pos_count = len(words & POSITIVE_WORDS)
    neg_count = len(words & NEGATIVE_WORDS)

    if pos_count > neg_count:
        label = "positive"
        score = 0.5 + 0.5 * (pos_count / (pos_count + neg_count + 1))
    elif neg_count > pos_count:
        label = "negative"
        score = 0.5 - 0.5 * (neg_count / (pos_count + neg_count + 1))
    else:
        label = "neutral"
        score = 0.5

    return {
        "label": label,
        "score": round(score, 3),
        "positive_words": pos_count,
        "negative_words": neg_count,
    }
