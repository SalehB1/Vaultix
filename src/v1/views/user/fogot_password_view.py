from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.util import await_only

from configurations.cbv import cbv
from configurations.db_config import get_db
from src.v1.schemas.forgot_password_schema import RequestPasswordResetEmail, RequestPasswordResetPhone, VerifyResetCode
from src.v1.services.forgot_password_service import UserService

forgot_password_router = APIRouter(prefix="/api/v1/user/forget", tags=["Forget Password"])


@cbv(forgot_password_router)
class UserController:
    db: AsyncSession = Depends(get_db)
    user_service = UserService()
    background_tasks: BackgroundTasks

    @forgot_password_router.post("/password/email")
    async def request_reset_email(self, request: RequestPasswordResetEmail):
        return await self.user_service.send_reset_code_email(str(request.Email), self.background_tasks)

    @forgot_password_router.post("/password/phone")
    async def request_reset_phone(self, request: RequestPasswordResetPhone):
        return await self.user_service.send_reset_code_phone(request.PhoneNumber, self.background_tasks)

    @forgot_password_router.post("/password/reset")
    async def reset_password(self, request: VerifyResetCode):
        return await self.user_service.verify_and_reset_password(
            code=request.Code,
            new_password=request.Password,
            email=request.Email,
            phone_number=request.PhoneNumber,
            background_tasks=self.background_tasks
        )
