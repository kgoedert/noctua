import os
import secrets
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


def get_api_token() -> str:
    token = os.getenv("NOCTUA_API_TOKEN")

    if not token:
        raise ValueError("NOCTUA_API_TOKEN not found.")

    return token


security = HTTPBearer()

API_TOKEN = get_api_token()


def get_http_bearer_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> str:

    if secrets.compare_digest(API_TOKEN, credentials.credentials):
        return credentials.credentials

    raise HTTPException(status_code=401, detail="Invalid authentication credentials")
