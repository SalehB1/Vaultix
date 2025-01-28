# src/v1/auth/views/profile/profile_auth.py

from fastapi import Depends, HTTPException
from sqlalchemy.orm.sync import update
from starlette import status
from configurations.cbv import cbv
from configurations.router import SlashInferringRouter
from src.v1.middlewares.auth_dependency import get_current_user
from src.v1.models.user import User
from src.v1.schemas.api_response_schema import APIResponse
from src.v1.schemas.profile_schema import ProfileResponse, UpdateEmailSchema, SendUpdateEmailSchema
from src.v1.services.profile_email_service import ProfileEmailService

user_email_router = SlashInferringRouter(prefix="/api/v1/user/profile", tags=["Profile Email Management"])


@cbv(user_email_router)
class UserPhoneView:
    current_user: User = Depends(get_current_user)
    profile_service = ProfileEmailService()

    @user_email_router.post("/email/change/send", response_model=APIResponse)
    async def send_update_code_email(
            self,
            in_data: SendUpdateEmailSchema,
    ):
        await self.profile_service.email_change_request_handler(
            user_id=str(self.current_user.uuid),
            new_email=str(in_data.Email),
        )

        return APIResponse(status_code=status.HTTP_202_ACCEPTED, detail='کد با موفقیت ارسال شد.')

    @user_email_router.patch("/email/verify", response_model=ProfileResponse)
    async def verify_email(
            self,
            in_data: UpdateEmailSchema,
    ):
        updated_user = await self.profile_service.update_email(
            user_id=str(self.current_user.uuid),
            new_email=str(in_data.Email),
            in_code=in_data.Code
        )

        return ProfileResponse(
            detail="ایمیل با موفقیت به‌روزرسانی شد",
            Email=updated_user.Email
        )
