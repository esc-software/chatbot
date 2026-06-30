import re

INJECTION_PATTERNS_EN = [
    "ignore previous",
    "system prompt",
    "reveal system",
    "bypass",
    "developer mode",
    "jailbreak",
    "you are a free",
    "do not follow",
    "new instructions",
    "override",
]

INJECTION_PATTERNS_PT = [
    "ignore instruções anteriores",
    "ignore as instruções",
    "modo desenvolvedor",
    "revelar sistema",
    "modo administrador",
    "você é um",
    "ignore tudo",
    "não siga",
]

INJECTION_PATTERNS = INJECTION_PATTERNS_EN + INJECTION_PATTERNS_PT


def detect_injection(text: str) -> bool:
    lower = text.lower()
    for pattern in INJECTION_PATTERNS:
        if pattern in lower:
            return True

    sql_patterns = [
        r"\bselect\b.*\bfrom\b",
        r"\bdrop\b\s+\btable\b",
        r"\bdelete\b.*\bfrom\b",
        r"\bunion\b.*\bselect\b",
        r"\binsert\b.*\binto\b",
        r"\bexec\b",
        r"\bxp_cmdshell\b",
        r"\bpg_sleep\b",
        r"\bwaitfor\b.*\bdelay\b",
    ]
    for pattern in sql_patterns:
        if re.search(pattern, lower):
            return True

    return False
