# src/v1/auth/views/login/google_auth.py
from fastapi import HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import Response

from configurations.OAuth import OAuthService
from configurations.cbv import cbv
from configurations.db_config import get_db
from configurations.router import SlashInferringRouter
from src.v1.models.user import AuthProvider
from src.v1.schemas.auth_schema import TokenDisplay
from src.v1.schemas.google_schema import AuthURLResponse
from src.v1.services.base_auth_service import AuthService
from src.v1.services.base_oauth_service import BaseOAuthService
from src.v1.services.cookie_service import set_auth_cookie
from src.v1.services.google_service import GoogleService

google_router = SlashInferringRouter(prefix="/api/v1/auth/google", tags=["Google Auth"])


@cbv(google_router)
class GoogleAuthView:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db
        self.auth_service = AuthService()
        self.oauth_service = OAuthService()
        self.google_service = GoogleService(self.oauth_service)
        self.base_oauth_service = BaseOAuthService()  # Initialize with db

    @google_router.get('/login', response_model=AuthURLResponse)
    async def login(self):
        """Returns Google OAuth URL"""
        return await self.google_service.get_login_url()

    @google_router.get('/callback', response_model=TokenDisplay)
    async def callback(self, code: str, response: Response):
        """Handle Google OAuth callback and user authentication"""
        try:
            # Get user data from Google
            oauth_data = await self.google_service.handle_callback(code)

            # Process OAuth authentication using BaseOAuthService
            user = await self.base_oauth_service.handle_oauth_authentication(
                oauth_data=oauth_data,
                provider=AuthProvider.GOOGLE
            )

            # Generate tokens
            access_token = await self.auth_service.token_service.create_access_token(
                str(user.uuid)
            )
            refresh_token = await self.auth_service.token_service.create_refresh_token(
                str(user.uuid)
            )

            await set_auth_cookie(
                response,
                access_token,
                refresh_token
            )

            return TokenDisplay(AccessToken=access_token, RefreshToken=refresh_token)

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Google authentication failed: {str(e)}"
            )
