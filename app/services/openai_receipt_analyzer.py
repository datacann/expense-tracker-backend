from openai import AsyncOpenAI
from app.config import settings
from app.schemas.receipt import ReceiptAnalysis
import logging

logger = logging.getLogger("receipts")

async def analyze_receipt_with_openai(image_bytes: bytes) -> ReceiptAnalysis:
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    # 1. Fotoğrafı Base64'e çevir (OpenAI gereksinimi)
    import base64
    base64_image = base64.b64encode(image_bytes).decode('utf-8')

    # 2. OpenAI isteği
    response = await client.chat.completions.parse(
        model=settings.OPENAI_RECEIPT_MODEL,
        messages=[
            {
                "role": "system",
                "content": """
                Fiş analiz et. 
                İşletme, tarih(YYYY-MM-DD), ürünler, tutarlar ve kategori(cat_food, cat_dining, cat_transport, cat_cleaning, cat_personal_care, cat_home, cat_entertainment, cat_shopping, cat_bills, cat_other) çıkar.
                currency alanı yalnızca TRY olmalıdır.
                Yapılandırılmış JSON döndür.
                """
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Bu fişi analiz et."},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                    }
                ]
            }
        ],
        response_format=ReceiptAnalysis,
    )

    analysis = response.choices[0].message.parsed
    if analysis is None:
        raise ValueError("OpenAI yapılandırılmış analiz döndürmedi")
    return analysis
