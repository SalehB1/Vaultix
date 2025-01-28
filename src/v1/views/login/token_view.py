from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.responses import Response

from configurations.cbv import cbv
from configurations.db_config import get_db
from configurations.router import SlashInferringRouter
from src.v1.schemas.auth_schema import TokenDisplay
from src.v1.services.base_auth_service import AuthService
from src.v1.services.cookie_service import set_auth_cookie
from src.v1.services.token_service import TokenService

refresh_router = SlashInferringRouter(prefix="/api/v1/token", tags=["Refresh Token"])


@cbv(refresh_router)
class TokensView:
    db: AsyncSession = Depends(get_db)
    token_service = TokenService()
    auth_service = AuthService()

    @refresh_router.post('/refresh', response_model=TokenDisplay )
    async def refresh_token(self, response: Response, request: Request):
        user = await self.token_service.create_token_from_refresh(request=request)
        access_token, refresh_token=await self.auth_service.create_tokens(user_id=str(user.uuid))

        await set_auth_cookie(
            response,
            access_token,
            refresh_token
        )

        return TokenDisplay(
            AccessToken=access_token,
            RefreshToken=refresh_token,
            TokenType='bearer'
        )