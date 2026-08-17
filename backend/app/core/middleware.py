import logging
import time
from uuid import uuid4

from fastapi import Request


logger = logging.getLogger("pmo_ai.request")


async def request_logging_middleware(
    request: Request,
    call_next,
):
    request_id = request.headers.get(
        "X-Request-ID",
        str(uuid4()),
    )

    request.state.request_id = request_id

    start_time = time.perf_counter()

    logger.info(
        "request_started | "
        "request_id=%s | "
        "method=%s | "
        "path=%s",
        request_id,
        request.method,
        request.url.path,
    )

    try:
        response = await call_next(request)

    except Exception:
        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        logger.exception(
            "request_failed | "
            "request_id=%s | "
            "method=%s | "
            "path=%s | "
            "duration_ms=%s",
            request_id,
            request.method,
            request.url.path,
            duration_ms,
        )

        raise

    duration_ms = round(
        (time.perf_counter() - start_time) * 1000,
        2,
    )

    response.headers["X-Request-ID"] = request_id

    logger.info(
        "request_completed | "
        "request_id=%s | "
        "method=%s | "
        "path=%s | "
        "status_code=%s | "
        "duration_ms=%s",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )

    return response