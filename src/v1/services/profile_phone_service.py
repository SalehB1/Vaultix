# src/v1/auth/services/auth/profile_service.py
import random
from datetime import timedelta

from fastapi import HTTPException
from starlette import status
from sqlalchemy import select

from configurations.cache import Cache
from configurations.db_config import get_db_outside

from typing import Optional

from configurations.environments import Values
from src.v1.models.user import User
from src.v1.services.email_service import send_email
from src.v1.services.otp_service import Otp


class ProfilePhoneService:
    otp_service = Otp()
    cache = Cache()

    async def __produce_phone_code(self, mobile: str, user_id: str):
        code = random.randint(100000, 999999)
        await self.cache.set(f'user:{user_id}-phone-change-{mobile}', code,
                             expire_time=timedelta(minutes=int(Values.PHONE_OTP_EXPIRE_TIME_MINUTES)))
        return code

    async def update_phone_step_one(self, user_id: str, phone_number: str, register: bool = False) -> bool:
        async with get_db_outside() as db:
            existing_user = await db.scalar(
                select(User).where(User.PhoneNumber == phone_number)
            )
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="این شماره تلفن قبلاً ثبت شده است"
                )
            else:
                code = await self.__produce_phone_code(mobile=phone_number, user_id=user_id)
                if register:
                    return await self.otp_service.send_register_new_phone_code(mobile=phone_number, code=code)
                else:
                    return await self.otp_service.send_change_phone_number_code(mobile=phone_number, code=code)

    async def verify_phone_change_code(self, user_id: str, mobile: str, code: str) -> bool:
        extracted_code = await self.cache.get(f'user:{user_id}-phone-change-{mobile}')
        if int(extracted_code) == int(code):
            await self.cache.delete(f'user:{user_id}-phone-change-{mobile}')
            return True
        else:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="کد وارد شده مورد قبول نیست"
            )

    async def verify_updated_phone_number(self, user_id: str, phone_number: str, code: str) -> User:
        verified = await self.verify_phone_change_code(user_id=user_id, mobile=phone_number, code=code)
        if verified:
            async with get_db_outside() as db:
                existing_user = await db.scalar(
                    select(User).where(User.PhoneNumber == phone_number)
                )
                if existing_user:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="این شماره تلفن قبلاً ثبت شده است"
                    )
                user = await db.scalar(
                    select(User).where(User.uuid == user_id, User.IsActive == True, User.is_deleted == False)
                )
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="کاربر یافت نشد"
                    )

                user.PhoneNumber = phone_number
                await db.commit()
                await db.refresh(user)
                return user