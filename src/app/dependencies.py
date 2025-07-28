import os
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

JWT_SECRET = os.getenv("JWT_SECRET", "secret")
auth_scheme = HTTPBearer()

class User:
    def __init__(self, user_id: str):
        self.id = user_id

async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(auth_scheme),
) -> User:
    try:
        payload = jwt.decode(creds.credentials, JWT_SECRET, algorithms=["HS256"])
        return User(payload["sub"])
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
