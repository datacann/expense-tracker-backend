import logging

logger = logging.getLogger("receipts")

from app.services.openai_receipt_analyzer import analyze_receipt_with_openai
from app.config import settings

async def analyze_receipt(image_bytes: bytes, request_id: str):
    if not settings.OPENAI_API_KEY.strip() or not settings.OPENAI_RECEIPT_MODEL.strip():
        raise RuntimeError("OpenAI sağlayıcısı yapılandırılmamış")
    
    return await analyze_receipt_with_openai(image_bytes)
