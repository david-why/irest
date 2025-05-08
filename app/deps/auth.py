from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from app import consts


async def verify_api_key(
    api_key: str | None = Depends(APIKeyHeader(name="X-API-Key", auto_error=False)),
) -> None:
    if consts.API_KEY is None:
        return
    if api_key != consts.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )
