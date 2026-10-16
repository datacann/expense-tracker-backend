from fastapi import APIRouter, UploadFile, File, Request
from fastapi.responses import JSONResponse
from app.services.receipt_analyzer import analyze_receipt
from app.schemas.receipt import ReceiptResponse
from app.config import settings
import uuid
import time
import logging

router = APIRouter()
logger = logging.getLogger("receipts")


def error_response(status_code: int, code: str, message: str, request_id: str):
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "requestId": request_id,
            }
        },
    )

@router.post("/receipts/analyze", response_model=ReceiptResponse)
async def analyze(request: Request, image: UploadFile = File(...)):
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    # Dosya boyutu kontrolü (basit)
    content = await image.read()
    if len(content) > settings.MAX_UPLOAD_BYTES:
        return error_response(
            413,
            "IMAGE_TOO_LARGE",
            "Fiş görseli izin verilen boyut sınırını aşıyor.",
            request_id,
        )

    if not settings.OPENAI_API_KEY.strip() or not settings.OPENAI_RECEIPT_MODEL.strip():
        return error_response(
            503,
            "SERVICE_UNAVAILABLE",
            "Fiş analiz servisi şu anda kullanılamıyor.",
            request_id,
        )
        
    try:
        analysis = await analyze_receipt(content, request_id)
        return {
            "schemaVersion": 1,
            "requestId": request_id,
            "analysis": analysis
        }
    except Exception as e:
        logger.error(f"Error {request_id}: {str(e)}")
        return error_response(
            503,
            "SERVICE_UNAVAILABLE",
            "Fiş analiz servisi şu anda kullanılamıyor.",
            request_id,
        )
