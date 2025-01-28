# src/v1/auth/views/login/phone_auth.py

from fastapi import Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import Response

from configurations.cbv import cbv
from configurations.db_config import get_db
from configurations.router import SlashInferringRouter
from src.v1.schemas.auth_schema import SendOtpSchema, PhoneOtpLoginDisplaySchema, TokenDisplay, VerifyOtpSchema
from src.v1.services.base_auth_service import AuthService
from src.v1.services.cookie_service import set_auth_cookie

local_router = SlashInferringRouter(prefix="/api/v1/auth", tags=["local auth phone"])


@cbv(local_router)
class LocalAuthView:
    db: AsyncSession = Depends(get_db)
    auth_service = AuthService()
    background_tasks: BackgroundTasks

    @local_router.post('/phone/otp-send', response_model=PhoneOtpLoginDisplaySchema)
    async def send_otp_code(self, in_data: SendOtpSchema):
        send_status = None
        user = await self.auth_service.multipurpose_login.get_user_by_phone(in_data.PhoneNumber)

        if user:
            self.background_tasks.add_task(self.auth_service.multipurpose_login.send_otp_code_phone,
                                           in_mobile=in_data.PhoneNumber)
            return PhoneOtpLoginDisplaySchema(detail='کد ورود با موفقیت ارسال شد!')

        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail='شماره همراه اشتباه یا ثبت نشده است.'
        )

    @local_router.post('/phone', response_model=TokenDisplay)
    async def login(self, response: Response, in_data: VerifyOtpSchema):
        try:
            user = await self.auth_service.multipurpose_login.login_with_phone(
                phone_number=in_data.PhoneNumber,
                code=in_data.Code
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

        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="خطای پردازش ؛ مجددا تلاش کنید"
            )
