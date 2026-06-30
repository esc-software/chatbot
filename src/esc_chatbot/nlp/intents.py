import json
from pathlib import Path

from ..config import settings

_DEFAULT_INTENTS: dict = {
    "intents": [
        {
            "tag": "saudacao",
            "patterns": ["oi", "olá", "e aí", "bom dia", "boa tarde", "boa noite"],
            "patterns_en": ["hello", "hi", "hey", "good morning", "good afternoon"],
            "responses": {
                "pt": ["Olá! Como posso ajudar hoje?", "Oi! Estou aqui para te auxiliar."],
                "en": ["Hello! How can I help you today?", "Hi! I'm here to assist you."],
            },
        },
        {
            "tag": "boas_vindas",
            "patterns": ["quem é você", "o que você faz", "o que é isso"],
            "patterns_en": ["who are you", "what do you do", "what is this"],
            "responses": {
                "pt": [
                    "Sou um assistente técnico para dúvidas e suporte sobre sistemas, desenvolvimento e segurança."
                ],
                "en": [
                    "I'm a technical assistant for questions and support about systems, development and security."
                ],
            },
        },
        {
            "tag": "ajuda_geral",
            "patterns": ["preciso de ajuda", "me ajuda", "não sei o que fazer"],
            "patterns_en": ["i need help", "help me", "i don't know what to do"],
            "responses": {
                "pt": ["Me descreva o problema com detalhes para eu te ajudar melhor."],
                "en": ["Describe the problem in detail so I can help you better."],
            },
        },
        {
            "tag": "encerramento",
            "patterns": ["tchau", "até mais", "encerrar", "finalizar"],
            "patterns_en": ["bye", "see you", "goodbye", "end"],
            "responses": {
                "pt": ["Tudo certo. Se precisar, estarei disponível."],
                "en": ["All set. I'll be here if you need me."],
            },
        },
        {
            "tag": "contato_suporte",
            "patterns": [
                "contato suporte", "falar com alguém", "suporte humano",
                "email suporte", "telefone suporte",
            ],
            "patterns_en": [
                "contact support", "talk to someone", "human support",
                "support email", "support phone",
            ],
            "responses": {
                "pt": [
                    "Você pode entrar em contato pelo e-mail hello@esc-software.com ou pelo telefone +55 11 99303-1311.",
                ],
                "en": [
                    "You can reach us at hello@esc-software.com or by phone at +55 11 99303-1311.",
                ],
            },
        },
        {
            "tag": "fallback",
            "patterns": [],
            "patterns_en": [],
            "responses": {
                "pt": ["Não consegui entender completamente. Pode reformular?"],
                "en": ["I didn't quite understand. Could you rephrase?"],
            },
        },
    ]
}


def _load_json(path: str) -> dict | None:
    p = Path(path)
    if not p.exists():
        return None
    try:
        with open(str(p), encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def load_intents() -> dict:
    data = _load_json(settings.intents_path)
    if data is not None:
        return data
    return _DEFAULT_INTENTS


INTENTS = load_intents()
