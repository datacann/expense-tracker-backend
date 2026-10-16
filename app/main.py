import uuid
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.routes import receipts, savings, voice

app = FastAPI(title="Expense Tracker API")

@app.middleware("http")
async def limit_savings_request_size(request: Request, call_next):
    if request.url.path == "/v1/savings/suggestions":
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > 16_384:
            request_id = str(uuid.uuid4())
            return JSONResponse(status_code=413, content={"error": {"code": "REQUEST_TOO_LARGE", "message": "Öneri isteği çok büyük.", "requestId": request_id}})
    return await call_next(request)

@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    request_id = str(uuid.uuid4())
    return JSONResponse(status_code=422, content={"error": {"code": "INVALID_REQUEST", "message": "İstek alanları geçersiz.", "requestId": request_id}})

app.include_router(receipts.router, prefix="/v1")
app.include_router(voice.router, prefix="/v1")
app.include_router(savings.router, prefix="/v1")

@app.get("/health")
async def health_check():
    return {"status": "ok"}
