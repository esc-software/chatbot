# Chatbot

> Official ESC Software website chatbot — an NLP-powered technical support assistant built with FastAPI, Word2Vec, and FAISS.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](pyproject.toml)

Try it live at **[esc-software.com](https://esc-software.com)**.

---

## Features

- **Intent classification** via Word2Vec + FAISS vector similarity
- **Optional bilingual translation** (Portuguese / English) via Google Translator — toggle with `ENABLE_TRANSLATION`
- **Injection protection** — detects prompt injection, jailbreak, SQL, and XSS attempts (English and Portuguese)
- **Rate limiting** — per-IP throttling
- **Conversation memory** — last N turns stored per user
- **Named Entity Recognition** — emails, phones, URLs, companies, money, numbers
- **Sentiment Analysis** — positive / negative / neutral classification
- **Spell correction** — normalizes common abbreviations ("vc" → "você", "td" → "tudo")
- **Async queue** — background processing for high concurrency via `POST /chat/queue`
- **Feedback system** — user ratings adjust intent confidence over time
- **Response diversity** — avoids repeating the same response twice in a row
- **Autotrain** — retrain the model from feedback and FAQ data
- **Docker ready** — full Docker and docker-compose support

## Quick Start

### Local

```bash
pip install -r requirements.txt
python -m src.esc_chatbot
```

### Docker

```bash
docker compose up --build
```

## Configuration

All configuration is done through environment variables. Copy `.env.example` to `.env` and adjust:

```bash
cp .env.example .env
```

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `HOST` | `0.0.0.0` | Server bind address |
| `PORT` | `3006` | Server port |
| `CORS_ORIGINS` | `https://esc-software.com,...` | Allowed CORS origins |
| `MAX_REQUESTS_PER_MIN` | `30` | Rate limit per IP |
| `FEEDBACK_WEBHOOK_URL` | — | Discord webhook for feedback notifications |
| `MEMORY_MAXLEN` | `15` | Conversation turns stored per user |
| `QUEUE_WORKERS` | `2` | Number of background queue workers |
| `QUEUE_MAX_SIZE` | `500` | Maximum queue size |
| `VECTOR_SIZE` | `60` | Word2Vec vector dimensions |
| `NLP_CONFIDENCE_THRESHOLD` | `0.55` | Minimum confidence for intent match |
| `ENABLE_TRANSLATION` | `true` | Enable automatic translation via Google Translate |
| `DEFAULT_LANG` | `pt` | Base language code for responses and NLP |
| `NER_ENABLE_EMAILS` | `true` | Extract email addresses from messages |
| `NER_ENABLE_PHONES` | `true` | Extract phone numbers from messages |
| `SPELL_ENABLED` | `true` | Enable spell correction |
| `SENTIMENT_ENABLED` | `true` | Enable sentiment analysis |
| `RESPONSE_DIVERSITY` | `true` | Avoid repeating the same response |
| `REDIS_URL` | — | Redis connection string (optional — enables persistent storage and distributed queue) |

## API

### `POST /chat`

```json
{"text": "Hello, how does support work?"}
```

Returns the matched intent, response text, confidence score, entities, sentiment, and conversation memory.

### `POST /chat/queue`

Same as `/chat` but processes asynchronously. Returns a `ticket_id` for polling.

### `GET /chat/queue/{ticket_id}`

Poll for the result of a queued request.

### `POST /feedback`

```json
{"text": "Great support!", "intent": "saudacao", "positive": true, "comment": ""}
```

Records user feedback and adjusts intent confidence.

### `POST /clear`

Clears the conversation history for the requesting IP.

### `POST /admin/train`

Retrains the NLP model using positive feedback and FAQ data.

### `GET /admin/faq`

Extracts frequently asked questions from chat logs.

### `GET /health`

Returns system health, version, model status, queue stats.

### `GET /help`

Lists available commands and intents.

## Project Structure

```
config/
└── intents.json    # Customize chatbot responses and trigger phrases
src/esc_chatbot/
├── main.py           # FastAPI application entrypoint
├── config.py         # Settings from environment
├── __main__.py       # CLI entrypoint (python -m)
├── nlp/              # NLP engine (Word2Vec + FAISS)
│   ├── engine.py     # NLPAttention class
│   ├── intents.py    # Intent loader (reads config/intents.json)
│   ├── preprocess.py # Text cleaning and translation
│   ├── lang_detect.py # Language detection (langdetect)
│   ├── spell.py      # Spell correction
│   ├── sentiment.py  # Sentiment analysis
│   └── ner.py        # Named Entity Recognition
├── api/              # HTTP layer
│   ├── routes.py     # Thin route handlers → delegates to services
│   └── middleware.py # Rate limiter
├── services/         # Business logic layer
│   ├── chat_service.py     # Chat processing pipeline
│   ├── feedback_service.py # Feedback + Discord webhook
│   └── admin_service.py    # Training + FAQ extraction
├── core/             # Cross-cutting concerns
│   ├── storage.py    # Memory & Feedback backends (file + Redis)
│   ├── security.py   # Injection detection
│   ├── queue.py      # Async task queue
│   └── log.py        # Structured logging
└── models/           # Pydantic schemas
```

## Tests

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

## Customizing the Chatbot

All chatbot responses and trigger phrases are in `config/intents.json`. Edit this file to change how the chatbot behaves.

### Intent structure

```json
{
  "tag": "saudacao",
  "patterns": ["oi", "olá", "bom dia"],
  "patterns_en": ["hello", "hi", "good morning"],
  "responses": {
    "pt": ["Olá! Como posso ajudar?", "Oi! Estou aqui."],
    "en": ["Hello! How can I help?", "Hi! I'm here."]
  }
}
```

| Field | Description |
| ----- | ----------- |
| `tag` | Unique intent identifier |
| `patterns` | Portuguese trigger phrases |
| `patterns_en` | English trigger phrases |
| `responses.pt` | Portuguese responses (randomly selected) |
| `responses.en` | English responses (randomly selected) |

After editing, regenerate the model:

```bash
python scripts/generate_model.py
```

To use a custom intents file:

```bash
INTENTS_PATH=my_intents.json python scripts/generate_model.py
```

If `config/intents.json` is missing or invalid, the built-in defaults are used.

## Generate Model

The NLP model is auto-generated on first startup. To pre-generate it:

```bash
python scripts/generate_model.py
```

## Reporting Vulnerabilities

If you find a security issue, please report it through our bug bounty program:

**https://security.esc-software.com**

## License

MIT © [ESC Software](https://esc-software.com)
