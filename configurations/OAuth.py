# oauth.py
from functools import lru_cache

from fastapi.security import OAuth2
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi import Request, HTTPException, status
from fastapi.security.utils import get_authorization_scheme_param
from typing import Optional, Dict
import json
from httpx import AsyncClient

from configurations.environments import Values


class OAuthConfig:
    GITHUB_CLIENT_ID = Values.GITHUB_CLIENT_ID
    GITHUB_CLIENT_SECRET = Values.GITHUB_CLIENT_SECRET
    GITHUB_REDIRECT_URI=Values.GITHUB_REDIRECT_URI
    GOOGLE_CLIENT_ID = Values.GOOGLE_CLIENT_ID
    GOOGLE_CLIENT_SECRET = Values.GOOGLE_CLIENT_SECRET
    GOOGLE_REDIRECT_URI = Values.GOOGLE_REDIRECT_URI
    COOKIE_NAME = Values.COOKIE_NAME


class OAuth2PasswordBearerWithCookie(OAuth2):
    def __init__(
            self,
            tokenUrl: str,
            scheme_name: Optional[str] = None,
            scopes: Optional[Dict[str, str]] = None,
            auto_error: bool = True,
    ):
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(flows=flows, scheme_name=scheme_name, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        userdata: str = request.cookies.get(OAuthConfig.COOKIE_NAME)
        if not userdata:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        userdata: json = json.loads(userdata)
        authorization: str = userdata.get("access_token")

        scheme, param = get_authorization_scheme_param(authorization)
        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            else:
                return None
        return param


class OAuthService:
    def __init__(self):
        self.config = OAuthConfig()
        self.http_client = AsyncClient()
