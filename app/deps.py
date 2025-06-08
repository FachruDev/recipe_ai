# app/deps.py

import time
from fastapi import Depends, Request, HTTPException, status
from sqlmodel import Session as DbSession
from app.db import get_db
from app.services.context_service import ContextService

## -- existing dependency untuk ContextService --
def get_context_service(
    db: DbSession = Depends(get_db)
) -> ContextService:
    return ContextService(db)


## -- NEW: in‐memory rate limiter dependency -- 
# Simple store: IP → list of request timestamps
_rate_limit_store: dict[str, list[float]] = {}
_RATE_LIMIT = 5      # max 5 requests
_WINDOW = 60         # per 60 detik

async def rate_limit(request: Request):
    ip = request.client.host or "unknown"
    now = time.time()
    # get new timestamps
    timestamps = _rate_limit_store.get(ip, [])
    # purge timestamps > window
    window_start = now - _WINDOW
    timestamps = [ts for ts in timestamps if ts > window_start]

    if len(timestamps) >= _RATE_LIMIT:
        # max limit
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too Many Requests"
        )

    # write this requests
    timestamps.append(now)
    _rate_limit_store[ip] = timestamps
