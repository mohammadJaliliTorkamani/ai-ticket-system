import logging
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from openai import APIConnectionError, APIStatusError, AuthenticationError, RateLimitError

from app.config import get_settings
from app.logging import configure_logging
from app.schemas import RespondRequest, RespondResponse
from app.services.openai_service import create_response
from app.services.rate_limit import enforce_rate_limit

configure_logging()
logger = logging.getLogger("ticketifier.api")
settings = get_settings()
docs_url = "/api/docs" if settings.api_docs_enabled and settings.environment != "production" else None
app = FastAPI(
    title="Ticketifier Request Workbench API",
    version="2.0.0",
    docs_url=docs_url,
    redoc_url=None,
    openapi_url="/api/openapi.json" if docs_url else None,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-Request-ID"],
)


def client_address(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "")
    return forwarded.split(",", 1)[0].strip() if forwarded else (request.client.host if request.client else "unknown")


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or str(uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Cache-Control"] = "no-store"
    return response


@app.exception_handler(Exception)
async def unhandled_exception(request: Request, exc: Exception):
    logger.exception("unhandled_request_error", extra={"request_id": request.state.request_id, "event": "request.failed"})
    return JSONResponse(status_code=500, content={"detail": "Internal server error", "request_id": request.state.request_id})


@app.get("/api/health/live", include_in_schema=False)
async def liveness():
    return {"status": "ok"}


@app.get("/api/health/ready", include_in_schema=False)
async def readiness():
    return {"status": "ready"}


@app.post("/api/respond", response_model=RespondResponse)
async def respond(payload: RespondRequest, request: Request, response: Response):
    if payload.model not in settings.models:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported model")
    remaining = await enforce_rate_limit(client_address(request))
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    request_id = request.state.request_id
    try:
        result = await create_response(payload.api_key.get_secret_value(), payload.model, payload.message)
    except AuthenticationError:
        raise HTTPException(status_code=401, detail="OpenAI rejected this API key") from None
    except RateLimitError:
        raise HTTPException(status_code=429, detail="OpenAI rate limit or quota reached for this key") from None
    except APIStatusError as exc:
        if exc.status_code == 403:
            raise HTTPException(status_code=403, detail="This key cannot use the selected model") from None
        raise HTTPException(status_code=502, detail="OpenAI returned an upstream error") from None
    except (APIConnectionError, TimeoutError):
        raise HTTPException(status_code=504, detail="OpenAI did not respond before the timeout") from None

    safe_input = {"api_key": "[REDACTED]", "message": payload.message, "model": payload.model}
    safe_output = {
        "status": "completed", "request_id": request_id, "model": payload.model,
        "latency_ms": result["latency_ms"], "output": result["output"], "usage": result["usage"],
    }
    transcript = [
        {"direction": "browser_to_ticketifier", "method": "POST", "path": "/api/respond", "headers": {"content-type": "application/json", "x-request-id": request_id}, "body": safe_input},
        {"direction": "ticketifier_to_openai", "method": "POST", "path": "/v1/responses", "headers": {"authorization": "Bearer [REDACTED]", "content-type": "application/json"}, "body": {"model": payload.model, "input": payload.message, "max_output_tokens": settings.max_output_tokens, "store": False}},
        {"direction": "openai_to_ticketifier", "status": 200, "path": "/v1/responses", "headers": {"x-request-id": result["provider_request_id"] or "unavailable"}, "body": {"status": "completed", "model": payload.model, "output": result["output"], "usage": result["usage"]}},
        {"direction": "ticketifier_to_browser", "status": 200, "path": "/api/respond", "headers": {"content-type": "application/json", "x-request-id": request_id}, "body": safe_output},
    ]
    logger.info("response_completed", extra={"request_id": request_id, "event": "response.completed"})
    return {**safe_output, "provider_request_id": result["provider_request_id"], "transcript": transcript}
