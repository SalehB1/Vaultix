from fastapi import Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import Response

from configurations.cbv import cbv
from configurations.db_config import get_db
from configurations.router import SlashInferringRouter
from src.v1.schemas.api_response_schema import APIResponse
from src.v1.schemas.auth_schema import MagicLinkEmailLoginSchema, TokenDisplay, MagicLinkEmailVerifySchema
from src.v1.services.base_auth_service import AuthService
from src.v1.services.cookie_service import set_auth_cookie

local_router = SlashInferringRouter(prefix="/api/v1/auth", tags=["MagicLink Auth"])


@cbv(local_router)
class LocalAuthView:
    def __init__(
            self,
            db: AsyncSession = Depends(get_db),
            background_tasks: BackgroundTasks = None
    ):
        self.db = db
        self.background_tasks = background_tasks
        self.auth_service = AuthService()

    @local_router.post('/magic', response_model=APIResponse)
    async def send_login_mail(self, in_data: MagicLinkEmailLoginSchema):
        user = await self.auth_service.multipurpose_login.get_user_by_email_for_magic_link(in_data.Email)
        if user:
            self.background_tasks.add_task(
                self.auth_service.magic_link_service.send_magic_link,
                user
            )
            return APIResponse(
                status_code=status.HTTP_202_ACCEPTED,
                detail='ایمیل ارسال شد'
            )
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail='ایمیل اشتباه یا در سیستم وجود ندارد'
        )

    @local_router.post('/magic/verify', response_model=TokenDisplay)
    async def verify_magic_link(self, response: Response, in_data: MagicLinkEmailVerifySchema):
        # try:
        user = await self.auth_service.magic_link_service.verify_magic_link(in_data.Token)
        access_token = await self.auth_service.token_service.create_access_token(str(user.uuid))
        refresh_token = await self.auth_service.token_service.create_refresh_token(str(user.uuid))

        await set_auth_cookie(
            response,
            access_token,
            refresh_token
        )

        return TokenDisplay(
            AccessToken=access_token,
            RefreshToken=refresh_token,
        )
