from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware

from .api.middleware import RateLimitMiddleware
from .api.routes import create_router
from .config import settings
from .core.queue import ChatQueue
from .core.storage import FeedbackBackend, MemoryBackend
from .nlp import NLPAttention
from .services.chat_service import process_chat

app = FastAPI(
    title="Chatbot API",
    description="Official ESC Software website chatbot — NLP-powered technical support assistant",
    version="1.0.0",
    contact={
        "name": "ESC Software",
        "email": "hello@esc-software.com",
        "url": "https://esc-software.com",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(RateLimitMiddleware)

engine = NLPAttention()
memory = MemoryBackend()
feedback_sys = FeedbackBackend()
queue = ChatQueue(
    lambda params, ip: process_chat(params, ip, engine, memory, feedback_sys)
)

app.include_router(create_router(engine, memory, feedback_sys, queue))
