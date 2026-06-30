import time

from fastapi import APIRouter, HTTPException, Request

from ..core.log import logger
from ..core.queue import ChatQueue, TaskStatus
from ..core.storage import FeedbackBackend, MemoryBackend
from ..models.schemas import FeedbackPayload, Message
from ..nlp import INTENTS
from ..services.admin_service import extract_faq, train
from ..services.chat_service import process_chat, validate_input
from ..services.feedback_service import record_feedback


def create_router(
    engine,
    memory: MemoryBackend,
    feedback_sys: FeedbackBackend,
    queue: ChatQueue,
) -> APIRouter:
    router = APIRouter()
    _start_time = time.time()

    @router.get("/health")
    def health() -> dict:
        return {
            "status": "ok",
            "version": "1.0.0",
            "uptime": round(time.time() - _start_time),
            "model_loaded": engine.is_loaded(),
            "memory_users": memory.count_users(),
            "total_feedback": feedback_sys.total_count(),
            "queue": queue.stats(),
        }

    @router.get("/help")
    def help_list() -> dict:
        return {
            "commands": [
                {"command": "/help", "description": "Show available commands"},
                {"command": "/clear", "description": "Clear your conversation history"},
                {
                    "command": "/feedback <positive/negative> [comment]",
                    "description": "Rate the last response",
                },
            ],
            "intents": [i["tag"] for i in INTENTS["intents"] if i["tag"] != "fallback"],
        }

    @router.post("/clear")
    def clear(request: Request) -> dict:
        ip = request.client.host if request.client else "unknown"
        memory.clear(ip)
        logger.info(ip, "clear", "command_clear", 1.0)
        return {"status": "ok", "message": "Conversation history cleared."}

    @router.post("/feedback")
    def feedback(payload: FeedbackPayload, request: Request) -> dict:
        ip = request.client.host if request.client else "unknown"
        return record_feedback(payload, ip, feedback_sys)

    @router.post("/chat")
    def chat(msg: Message, request: Request) -> dict:
        ip = request.client.host if request.client else "unknown"

        ok, result = validate_input(msg.text)
        if not ok:
            logger.warn(ip, msg.text, f"validation_failed:{result}")
            return {"response": "Invalid input.", "error": result}

        return process_chat({"text": result}, ip, engine, memory, feedback_sys)

    @router.post("/chat/queue")
    def chat_enqueue(msg: Message, request: Request) -> dict:
        ip = request.client.host if request.client else "unknown"

        ok, result = validate_input(msg.text)
        if not ok:
            logger.warn(ip, msg.text, f"validation_failed:{result}")
            return {"response": "Invalid input.", "error": result}

        task_id = queue.enqueue({"text": result}, ip)
        if task_id is None:
            raise HTTPException(status_code=503, detail="Queue is full")

        return {"ticket_id": task_id, "status": "queued"}

    @router.get("/chat/queue/{ticket_id}")
    def chat_result(ticket_id: str) -> dict:
        task = queue.get_result(ticket_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Ticket not found")

        if task.status == TaskStatus.PENDING:
            return {"ticket_id": ticket_id, "status": "pending"}
        if task.status == TaskStatus.PROCESSING:
            return {"ticket_id": ticket_id, "status": "processing"}
        if task.status == TaskStatus.FAILED:
            return {"ticket_id": ticket_id, "status": "failed", "error": task.error}
        if task.status == TaskStatus.DONE:
            return {"ticket_id": ticket_id, "status": "done", "result": task.result}
        return {"ticket_id": ticket_id, "status": "unknown"}

    @router.post("/admin/train")
    def admin_train(request: Request) -> dict:
        ip = request.client.host if request.client else "unknown"
        return train(engine, ip)

    @router.get("/admin/faq")
    def admin_faq(request: Request) -> dict:
        ip = request.client.host if request.client else "unknown"
        return extract_faq(engine, ip)

    return router
