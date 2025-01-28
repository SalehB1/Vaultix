# src/v1/auth/services/auth/cookie_service.py

from fastapi import Response
import json
from configurations.OAuth import OAuthConfig
from configurations.environments import Values

async def set_auth_cookie(response: Response, access_token: str, refresh_token: str):
    cookie_value = {
        "access_token": f"bearer {access_token}",
        "refresh_token": f"bearer {refresh_token}"
    }
    if Values.RUN_MODE == 'main':
        response.set_cookie(
            key=OAuthConfig.COOKIE_NAME,
            value=json.dumps(cookie_value),
            httponly=True,
            samesite="none",
            domain=Values.COOKIE_URL,
            secure=True,
        )
    else:
        response.set_cookie(
            key=OAuthConfig.COOKIE_NAME,
            value=json.dumps(cookie_value),
            domain=None,
            httponly=True,
        )