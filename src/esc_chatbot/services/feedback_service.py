import requests

from ..config import settings
from ..core.log import logger
from ..models.schemas import FeedbackPayload


def record_feedback(payload: FeedbackPayload, ip: str, feedback_sys) -> dict:
    feedback_sys.record(
        user=ip,
        text=payload.text,
        intent=payload.intent,
        positive=payload.positive,
        comment=payload.comment,
    )

    logger.info(
        ip,
        payload.text,
        f"feedback_{payload.intent}",
        1.0 if payload.positive else 0.0,
    )

    if settings.feedback_webhook_url:
        label = "positive" if payload.positive else "negative"
        data = {
            "content": (
                f"\U0001f4ac **New Feedback**\n\n"
                f"\U0001f464 User: `{ip}`\n"
                f"\U0001f3af Intent: `{payload.intent}`\n"
                f"\U0001f4d7 Text: {payload.text}\n"
                f"\U0001f7e2 Label: **{label}**\n"
                + (f"\U0001f4dd Comment: {payload.comment}" if payload.comment else "")
            )
        }
        try:
            requests.post(settings.feedback_webhook_url, json=data, timeout=5)
        except requests.RequestException:
            logger.warn(ip, payload.text, "feedback_webhook_failed")

    return {
        "status": "ok",
        "intent_stats": feedback_sys.intent_stats(payload.intent),
    }
