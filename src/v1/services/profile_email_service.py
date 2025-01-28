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


class ProfileEmailService:
    otp_service = Otp()
    cache = Cache()

    async def __verify_email_change_code(self, user_id: str, email: str, code: str) -> bool:
        extracted_code = await self.cache.get(f'user:{user_id}-email-change-{email}')
        if not extracted_code:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="درخواست یافت نشد ! ؛ مجددا تلاش کنید"
            )
        if int(extracted_code) == int(code):
            await self.cache.delete(f'user:{user_id}-phone-change-{email}')
            return True
        else:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="کد وارد شده مورد قبول نیست"
            )

    async def __produce_email_code(self, email: str, user_id: str):
        verification_code = str(random.randint(100000, 999999))
        digits_dict = {f'd{i + 1}': int(digit) for i, digit in enumerate(verification_code)}
        await self.cache.set(key=
                             f'user:{user_id}-email-change-{email}', value=
                             verification_code,
                             expire_time=timedelta(minutes=int(Values.EMAIL_CHANGE_OTP_EXPIRE_TIME_MINUTES))
                             )

        return digits_dict

    async def email_change_request_handler(self, user_id: str, new_email: str) -> bool:
        async with get_db_outside() as db:
            existing_user = await db.scalar(
                select(User).where(User.Email == new_email)
            )
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="امکان استفاده از این ایمیل وجود ندارد."
                )
            user = await db.scalar(
                select(User).where(User.uuid == user_id)
            )
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="کاربر یافت نشد"
                )
            if user.is_oauth_user:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="شما مجاز به تغییر ایمیل خود نمی باشید"
                )
        digits_dict = await self.__produce_email_code(email=new_email, user_id=user_id)
        template_body = {
            'company': f"{Values.COMPANY_NAME}",
            'd1': digits_dict['d6'],
            'd2': digits_dict['d5'],
            'd3': digits_dict['d4'],
            'd4': digits_dict['d3'],
            'd5': digits_dict['d2'],
            'd6': digits_dict['d1'],
            'minutes': Values.EMAIL_CHANGE_OTP_EXPIRE_TIME_MINUTES
        }

        r = await send_email(
            subject="درخواست تغییر ایمیل",
            recipients=[user.Email],
            template_name="verify-email.html",
            template_body=template_body,
            sender_name="Company-name",
            sender_email="verify@Hooshinai.com",
            html=True
        )
        print(r)
        return True

    async def update_email(self, user_id: str, new_email: str, in_code: str) -> User:
        await self.__verify_email_change_code(user_id=user_id, email=new_email, code=in_code)
        async with get_db_outside() as db:
            existing_user = await db.scalar(
                select(User).where(User.Email == new_email)
            )
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="امکان استفاده از این ایمیل وجود ندارد."
                )
            user = await db.scalar(
                select(User).where(User.uuid == user_id)
            )
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="کاربر یافت نشد"
                )
            if user.is_oauth_user:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="شما مجاز به تغییر ایمیل خود نمی باشید"
                )
            try:
                user.Email = new_email
                await db.commit()
                await db.refresh(user)
            except Exception as e:
                print(e)
                await db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail='مشکلی در تغییر ایمیل به وجود آمد ، لطفا دوباره شروع کنید'
                )
            return user

if __name__ == '__main__':
    # Method 1: Generate full number then split into dict
    code = str(random.randint(100000, 999999))
    code_dict = {f'd{i + 1}': int(digit) for i, digit in enumerate(code)}

    # Method 2: Generate each digit separately
    a = {f'd{i + 1}': random.randint(0, 9) for i in range(6)}
    print(a)
