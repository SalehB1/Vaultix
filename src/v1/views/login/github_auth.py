# src/v1/auth/views/login/github_auth.py

from fastapi import Depends, Response
from configurations.OAuth import OAuthService
from configurations.cbv import cbv
from configurations.router import SlashInferringRouter
from src.v1.schemas.auth_schema import TokenDisplay
from src.v1.schemas.github_schema import AuthURLResponse
from src.v1.services.cookie_service import set_auth_cookie
from src.v1.services.github_service import GitHubService
from src.v1.services.base_auth_service import AuthService
from src.v1.services.base_oauth_service import BaseOAuthService
from src.v1.models.user import AuthProvider
from sqlalchemy.ext.asyncio import AsyncSession
from configurations.db_config import get_db

github_router = SlashInferringRouter(prefix="/api/v1/auth/github", tags=["github auth"])


@cbv(github_router)
class GitHubAuthView:
    def __init__(self, db: AsyncSession = Depends(get_db)):
        self.db = db
        self.auth_service = AuthService()
        self.oauth_service = OAuthService()
        self.github_service = GitHubService(self.oauth_service)
        self.base_oauth_service = BaseOAuthService()

    @github_router.get('/login', response_model=AuthURLResponse)
    async def login(self):
        """Returns GitHub OAuth URL"""
        return await self.github_service.get_login_url()

    @github_router.get('/callback', response_model=TokenDisplay)
    async def callback(self, code: str, response: Response):
        """Handle GitHub OAuth callback and user authentication"""
        # try:
            # Get user data from GitHub
        oauth_data = await self.github_service.handle_callback(code)

        # Process OAuth authentication using BaseOAuthService
        user = await self.base_oauth_service.handle_oauth_authentication(
            oauth_data=oauth_data,
            provider=AuthProvider.GITHUB
        )

        # Generate tokens
        access_token = await self.auth_service.token_service.create_access_token(
            str(user.uuid)
        )
        refresh_token = await self.auth_service.token_service.create_refresh_token(
            str(user.uuid)
        )

        # Set cookie
        await set_auth_cookie(
            response,
            access_token,
            refresh_token
        )

        return TokenDisplay(AccessToken=access_token,RefreshToken=refresh_token)

        # except Exception as e:
        #     raise HTTPException(
        #         status_code=status.HTTP_401_UNAUTHORIZED,
        #         detail=f"GitHub authentication failed: {str(e)}"
        #     )