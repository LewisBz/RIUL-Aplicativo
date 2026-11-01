import time
from collections import defaultdict, deque
from functools import wraps

from flask import current_app, request

from app.utils.errors import ServiceError

_hits: dict[str, deque] = defaultdict(deque)


def reset_rate_limits() -> None:
    _hits.clear()


def rate_limit(max_calls: int, per_seconds: int):
    """Limita peticiones por IP y endpoint (memoria del proceso)."""

    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not current_app.config.get("RATELIMIT_ENABLED", True):
                return view(*args, **kwargs)
            key = f"{request.remote_addr}:{request.endpoint}"
            now = time.monotonic()
            window = _hits[key]
            while window and now - window[0] > per_seconds:
                window.popleft()
            if len(window) >= max_calls:
                raise ServiceError(
                    "Demasiados intentos. Intenta de nuevo en unos minutos.", 429
                )
            window.append(now)
            return view(*args, **kwargs)

        return wrapped

    return decorator
