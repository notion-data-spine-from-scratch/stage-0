import os

import httpx
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

JWT_SECRET = os.getenv("JWT_SECRET", "secret")
KRATOS_URL = os.getenv("KRATOS_PUBLIC_URL", "http://kratos:4433")
auth_scheme = HTTPBearer()


class User:
    def __init__(self, user_id: str):
        self.id = user_id


async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(auth_scheme),
) -> User:
    try:
        # Validate token with Kratos
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{KRATOS_URL}/sessions/whoami",
                headers={"Cookie": f"ory_kratos_session={creds.credentials}"},
            )
        resp.raise_for_status()
        data = resp.json()
        return User(data["identity"]["id"])
    except Exception:
        # Fallback to local secret for tests
        try:
            payload = jwt.decode(creds.credentials, JWT_SECRET, algorithms=["HS256"])
            return User(payload["sub"])
        except Exception:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
