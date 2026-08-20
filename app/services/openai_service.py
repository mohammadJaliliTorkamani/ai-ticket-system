import asyncio
import time

from openai import OpenAI

from app.config import get_settings


async def create_response(api_key: str, model: str, message: str) -> dict:
    settings = get_settings()

    def call_openai() -> dict:
        started = time.perf_counter()
        client = OpenAI(api_key=api_key, timeout=settings.request_timeout_seconds, max_retries=1)
        response = client.responses.create(
            model=model,
            input=message,
            max_output_tokens=settings.max_output_tokens,
            store=False,
        )
        usage = response.usage
        return {
            "output": response.output_text,
            "provider_request_id": getattr(response, "_request_id", None),
            "latency_ms": round((time.perf_counter() - started) * 1000),
            "usage": {
                "input_tokens": getattr(usage, "input_tokens", 0) if usage else 0,
                "output_tokens": getattr(usage, "output_tokens", 0) if usage else 0,
                "total_tokens": getattr(usage, "total_tokens", 0) if usage else 0,
            },
        }

    return await asyncio.wait_for(asyncio.to_thread(call_openai), timeout=settings.request_timeout_seconds + 5)
