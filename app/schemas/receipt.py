from pydantic import BaseModel, Field
from datetime import date as Date
from typing import List, Literal, Optional

class ReceiptItem(BaseModel):
    rawText: str
    description: str
    amountMinor: Optional[int] = Field(None, ge=0)
    categoryId: Optional[str] = None

class ReceiptAnalysis(BaseModel):
    merchant: Optional[str] = None
    date: Optional[Date] = None
    currency: Literal["TRY"] = "TRY"
    totalMinor: Optional[int] = Field(None, ge=0)
    items: List[ReceiptItem]
    warnings: List[str] = []
    isSample: bool = False

class ReceiptResponse(BaseModel):
    schemaVersion: int = 1
    requestId: str
    analysis: ReceiptAnalysis
