import re

COMMON_CORRECTIONS: dict[str, str] = {
    "td": "tudo",
    "vc": "você",
    "tb": "também",
    "pq": "porque",
    "pra": "para",
    "q": "que",
    "eh": "é",
    "ta": "está",
    "to": "estou",
    "nao": "não",
    "ja": "já",
    "so": "só",
    "mais": "mas",
    "cmg": "comigo",
    "blz": "beleza",
    "obg": "obrigado",
    "vlw": "valeu",
    "mt": "muito",
    "ngm": "ninguém",
    "pqp": "",
    "ctz": "certeza",
    "msg": "mensagem",
    "vdd": "verdade",
    "plmdds": "pelo amor de deus",
    "mds": "meu deus",
    "urk": "url",
    "hrs": "horas",
    "min": "minutos",
    "seg": "segundos",
    "dps": "depois",
    "aki": "aqui",
    "akis": "aqui",
}

_RE_VC = re.compile(r"\bvc\b")
_RE_Q = re.compile(r"\bq\b")
_RE_TA = re.compile(r"\bta\b")


def correct(text: str) -> str:
    tokens = text.lower().split()
    corrected = [COMMON_CORRECTIONS.get(t, t) for t in tokens]
    result = " ".join(corrected)

    result = _RE_VC.sub("você", result)
    result = _RE_Q.sub("que", result)
    result = _RE_TA.sub("está", result)

    return result
