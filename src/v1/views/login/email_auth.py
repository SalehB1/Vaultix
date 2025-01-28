# src/v1/auth/views/login/email_auth.py

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request
from starlette.responses import Response

from configurations.cbv import cbv
from configurations.db_config import get_db
from configurations.environments import Values
from configurations.router import SlashInferringRouter
from src.v1.schemas.auth_schema import TokenDisplay, EmailPassLoginSchema, LogoutDisplaySchema
from src.v1.services.base_auth_service import AuthService
from src.v1.services.cookie_service import set_auth_cookie

local_router = SlashInferringRouter(prefix="/api/v1/auth", tags=["local Auth Email"])


@cbv(local_router)
class LocalAuthView:
    db: AsyncSession = Depends(get_db)
    auth_service = AuthService()

    @local_router.post('/email', response_model=TokenDisplay)
    async def login(self, response: Response, in_data: EmailPassLoginSchema):
        try:
            user = await self.auth_service.multipurpose_login.login_with_email(
                str(in_data.Email),
                in_data.Password
            )

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

            return TokenDisplay(
                AccessToken=access_token,
                RefreshToken=refresh_token,
                TokenType='bearer'
            )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="مشکل در ورود لطفا مقادیر خود را بررسی کنید"
            )

    # @local_router.post('/logout')
    @local_router.post('/logout', response_model=LogoutDisplaySchema, tags=['token'])
    async def logout(self, response: Response, request: Request):
        if not request.cookies.get(Values.COOKIE_NAME):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Not Logged In or You are not authorized to perform this action")

        response.delete_cookie(key=Values.COOKIE_NAME)
        return LogoutDisplaySchema(detail="Logged Out")
