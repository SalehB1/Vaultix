# src/v1/auth/views/profile/profile_auth.py

from fastapi import Depends, HTTPException
from starlette import status
from configurations.cbv import cbv
from configurations.router import SlashInferringRouter
from src.v1.middlewares.auth_dependency import get_current_user
from src.v1.models.user import User
from src.v1.schemas.api_response_schema import APIResponse
from src.v1.schemas.profile_schema import ProfileResponse, UpdatePhoneSchema, UpdateEmailSchema, SendPhoneCodeSchema
from src.v1.services.profile_phone_service import ProfilePhoneService

user_phone_router = SlashInferringRouter(prefix="/api/v1/user/profile", tags=["Profile Phone Management"])


@cbv(user_phone_router)
class UserPhoneView:
    current_user: User = Depends(get_current_user)
    profile_service = ProfilePhoneService()


    @user_phone_router.post("/phone/set/send-code", response_model=APIResponse)
    async def send_code_for_update_phone_number(
            self,
            in_data: SendPhoneCodeSchema,
    ):
        await self.profile_service.update_phone_step_one(
            user_id=str(self.current_user.uuid),
            phone_number=in_data.PhoneNumber,
            register=True
        )

        return APIResponse(status_code=status.HTTP_202_ACCEPTED, detail='کد با موفقیت ارسال شد.')

    @user_phone_router.post("/phone/change/send-code", response_model=APIResponse)
    async def change_exist_phone_number(self,in_data: SendPhoneCodeSchema,):
        await self.profile_service.update_phone_step_one(
            user_id=str(self.current_user.uuid),
            phone_number=in_data.PhoneNumber,
        )

        return APIResponse(status_code=status.HTTP_202_ACCEPTED, detail='کد با موفقیت ارسال شد.')

    @user_phone_router.patch("/phone-number/verify", response_model=ProfileResponse)
    async def verify_new_phone_number(
            self,
            in_data: UpdatePhoneSchema,
    ):
        updated_user = await self.profile_service.verify_updated_phone_number(
            user_id=str(self.current_user.uuid),
            phone_number=in_data.PhoneNumber,
            code=in_data.Code
        )
        return ProfileResponse(
            detail="شماره همراه با موفقیت به‌ ثبت شد",
            PhoneNumber=updated_user.PhoneNumber
        )

