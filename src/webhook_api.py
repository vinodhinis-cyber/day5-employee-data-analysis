import hashlib
import hmac
import logging
import os

from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Request

load_dotenv()

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

if not WEBHOOK_SECRET:
    raise ValueError("WEBHOOK_SECRET is missing from .env")

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Webhook Receiver",
    description="Receives and verifies customer events",
    version="1.0.0",
)


def process_event(event_body: bytes):
    logger.info("Customer event received: %s", event_body.decode("utf-8"))


@app.post("/webhooks/customer-events")
async def receive_customer_event(
    request: Request,
    background_tasks: BackgroundTasks,
    x_signature: str = Header(default=None, alias="X-Signature"),
):
    raw_body = await request.body()

    if not x_signature:
        raise HTTPException(status_code=401, detail="Missing signature")

    expected_signature = hmac.new(
        WEBHOOK_SECRET.encode("utf-8"), raw_body, hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected_signature, x_signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    background_tasks.add_task(process_event, raw_body)

    return {"status": "accepted"}
