import logging
import uuid
from typing import Literal

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from app.config import settings

router = APIRouter()
logger = logging.getLogger("voice")


class VoiceExtraction(BaseModel):
    isValid: bool
    description: str | None = None
    amountMinor: int | None = Field(default=None, gt=0)
    categoryId: Literal[
        "cat_food",
        "cat_dining",
        "cat_transport",
        "cat_cleaning",
        "cat_personal_care",
        "cat_home",
        "cat_entertainment",
        "cat_shopping",
        "cat_bills",
        "cat_other",
    ] | None = None


def error_response(status_code: int, code: str, message: str, request_id: str):
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message, "requestId": request_id}},
    )


@router.post("/voice/analyze")
async def analyze_voice(audio: UploadFile = File(...)):
    request_id = str(uuid.uuid4())
    if not settings.OPENAI_API_KEY.strip():
        return error_response(503, "SERVICE_UNAVAILABLE", "Ses analiz servisi şu anda kullanılamıyor.", request_id)

    content = await audio.read()
    if not content:
        return error_response(400, "INVALID_AUDIO", "Ses kaydı boş.", request_id)

    try:
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        transcript = await client.audio.transcriptions.create(
            model="whisper-1",
            file=(audio.filename or "recording.m4a", content, audio.content_type or "audio/mp4"),
            language="tr",
            temperature=0,
        )
        transcript_text = transcript.text.strip()
        if not transcript_text:
            return error_response(422, "UNREADABLE_AUDIO", "Ses kaydında anlaşılır bir ifade bulunamadı.", request_id)

        response = await client.chat.completions.parse(
            model=settings.OPENAI_RECEIPT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Türkçe metindeki harcamayı yalnızca açıkça söylenen bilgilerden çıkar. "
                        "Açıklama ve pozitif bir tutar ikisi de açıkça yoksa isValid=false döndür; "
                        "eksik değerleri tahmin etme, varsayılan kahve/market veya tutar uydurma. "
                        "Geçerliyse isValid=true, açıklama, integer kuruş amountMinor ve uygun categoryId döndür. "
                        "Para birimi TRY'dir."
                    ),
                },
                {"role": "user", "content": transcript_text},
            ],
            response_format=VoiceExtraction,
        )
        analysis = response.choices[0].message.parsed
        if analysis is None:
            raise ValueError("Yapılandırılmış ses analizi dönmedi")
        if (
            not analysis.isValid
            or not analysis.description
            or analysis.amountMinor is None
            or analysis.categoryId is None
        ):
            return error_response(
                422,
                "UNREADABLE_AUDIO",
                "Açıklama ve tutar net anlaşılamadı. Lütfen ikisini de söyleyerek tekrar deneyin.",
                request_id,
            )
        return {
            "requestId": request_id,
            "transcript": transcript_text,
            "analysis": {
                "description": analysis.description,
                "amountMinor": analysis.amountMinor,
                "categoryId": analysis.categoryId,
            },
        }
    except Exception as error:
        logger.error("Voice analysis failed %s: %s", request_id, str(error))
        return error_response(503, "SERVICE_UNAVAILABLE", "Ses analiz servisi şu anda kullanılamıyor.", request_id)
