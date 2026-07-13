import time
from typing import Any

from fastapi.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send


class RateLimitMiddleware:
    def __init__(self, app: ASGIApp, max_requests: int = 120, window_seconds: int = 60) -> None:
        self.app = app
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.storage: dict[str, dict[str, Any]] = {}

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        client_ip = scope.get("client", ["unknown"])[0]
        if client_ip is None:
            client_ip = "unknown"

        now = time.time()
        item = self.storage.get(client_ip, {"count": 0, "window_start": now})

        if now - item["window_start"] > self.window_seconds:
            item = {"count": 0, "window_start": now}

        item["count"] += 1
        self.storage[client_ip] = item

        if item["count"] > self.max_requests:
            response = JSONResponse(
                status_code=429,
                content={"detail": "Too many requests, please try again later."},
            )
            await response(scope, receive, send)
            return

        await self.app(scope, receive, send)
