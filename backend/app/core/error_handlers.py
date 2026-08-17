import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


logger = logging.getLogger("pmo_ai.error")


def register_exception_handlers(
    app: FastAPI,
):
    @app.exception_handler(Exception)
    async def unexpected_exception_handler(
        request: Request,
        exc: Exception,
    ):
        request_id = getattr(
            request.state,
            "request_id",
            "unknown",
        )

        logger.exception(
            "unhandled_exception | "
            "request_id=%s | "
            "method=%s | "
            "path=%s | "
            "error=%s",
            request_id,
            request.method,
            request.url.path,
            str(exc),
        )

        return JSONResponse(
            status_code=500,
            content={
                "detail": (
                    "An unexpected server error occurred"
                ),
                "request_id": request_id,
            },
        )