import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Settings:
    host: str = field(default_factory=lambda: os.getenv("HOST", "0.0.0.0"))
    port: int = field(
        default_factory=lambda: int(os.getenv("PORT", "3006"))
    )
    cors_origins: list[str] = field(default_factory=lambda: [
        o.strip()
        for o in os.getenv(
            "CORS_ORIGINS",
            "https://esc-software.com,https://www.esc-software.com",
        ).split(",")
        if o.strip()
    ])
    max_requests_per_min: int = field(
        default_factory=lambda: int(os.getenv("MAX_REQUESTS_PER_MIN", "30"))
    )
    feedback_webhook_url: str = field(
        default_factory=lambda: os.getenv("FEEDBACK_WEBHOOK_URL", "")
    )

    queue_workers: int = field(
        default_factory=lambda: int(os.getenv("QUEUE_WORKERS", "2"))
    )
    queue_max_size: int = field(
        default_factory=lambda: int(os.getenv("QUEUE_MAX_SIZE", "500"))
    )

    memory_maxlen: int = field(
        default_factory=lambda: int(os.getenv("MEMORY_MAXLEN", "15"))
    )
    vector_size: int = field(
        default_factory=lambda: int(os.getenv("VECTOR_SIZE", "60"))
    )
    nlp_confidence_threshold: float = field(
        default_factory=lambda: float(
            os.getenv("NLP_CONFIDENCE_THRESHOLD", "0.55")
        )
    )
    enable_translation: bool = field(
        default_factory=lambda: os.getenv("ENABLE_TRANSLATION", "true").lower()
        in ("true", "1", "yes")
    )
    default_lang: str = field(
        default_factory=lambda: os.getenv("DEFAULT_LANG", "pt")
    )

    ner_enable_emails: bool = field(
        default_factory=lambda: os.getenv("NER_ENABLE_EMAILS", "true").lower()
        in ("true", "1", "yes")
    )
    ner_enable_phones: bool = field(
        default_factory=lambda: os.getenv("NER_ENABLE_PHONES", "true").lower()
        in ("true", "1", "yes")
    )
    ner_enable_urls: bool = field(
        default_factory=lambda: os.getenv("NER_ENABLE_URLS", "true").lower()
        in ("true", "1", "yes")
    )
    ner_enable_money: bool = field(
        default_factory=lambda: os.getenv("NER_ENABLE_MONEY", "true").lower()
        in ("true", "1", "yes")
    )
    sentiment_enabled: bool = field(
        default_factory=lambda: os.getenv("SENTIMENT_ENABLED", "true").lower()
        in ("true", "1", "yes")
    )
    spell_enabled: bool = field(
        default_factory=lambda: os.getenv("SPELL_ENABLED", "true").lower()
        in ("true", "1", "yes")
    )
    redis_url: str = field(
        default_factory=lambda: os.getenv("REDIS_URL", "")
    )
    response_diversity: bool = field(
        default_factory=lambda: os.getenv("RESPONSE_DIVERSITY", "true").lower()
        in ("true", "1", "yes")
    )

    intents_path: str = field(
        default_factory=lambda: os.getenv(
            "INTENTS_PATH", "config/intents.json"
        )
    )
    log_file: str = "logs/chat_logs.jsonl"
    memory_file: str = "storage/memory.json"
    feedback_file: str = "storage/feedback.jsonl"
    w2v_path: str = "storage/w2v.model"
    faiss_path: str = "storage/faiss.index"
    meta_path: str = "storage/meta.json"
    faq_file: str = "storage/faq.json"


settings = Settings()
