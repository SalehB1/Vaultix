from typing import Optional
from datetime import timedelta
import random

from sqlalchemy import select
from fastapi import HTTPException, BackgroundTasks
from configurations.cache import Cache
from configurations.db_config import get_db_outside
from configurations.environments import Values
from src.v1.models.user import User

from src.v1.services.email_service import send_email
from src.v1.services.otp_service import Otp
from src.v1.services.password_service import PasswordService


class UserService:
    def __init__(self):
        self.cache = Cache()
        self.code_expiry = timedelta(minutes=int(Values.FORGET_PASSWORD_CODE_EXPIRE_TIME_MINUTES))
        self.password_service = PasswordService()
        self.sms_controller = Otp()

    @staticmethod
    async def get_user_by_email(email: str) -> Optional[User]:
        async with get_db_outside() as db:
            return await db.scalar(select(User).where(User.Email == email))

    @staticmethod
    async def get_user_by_phone(phone_number: str) -> Optional[User]:
        async with get_db_outside() as db:
            return await db.scalar(select(User).where(User.PhoneNumber == phone_number))

    @staticmethod
    async def __produce_email_code():
        verification_code = str(random.randint(100000, 999999))
        digits_dict = {f'd{i + 1}': int(digit) for i, digit in enumerate(verification_code)}
        return digits_dict, verification_code

    @staticmethod
    async def generate_verification_code() -> str:
        return ''.join(random.choices('0123456789', k=6))

    @staticmethod
    async def get_cache_key(identifier: str) -> str:
        return f"password_reset_{identifier}"

    @staticmethod
    async def verify_local_user(user: User):
        if not user.is_local_user:
            raise HTTPException(
                status_code=400,
                detail=f"لطفاً از {user.AuthProvider} برای ورود به حساب خود استفاده کنید"
            )

    async def send_reset_code_email(self, email: str, background_tasks: BackgroundTasks) -> dict:
        user = await self.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=404, detail="اطلاعات وارد شده وجود ندارد یا اشتباه است.")

        await self.verify_local_user(user)

        digits_dict, code = await self.__produce_email_code()
        cache_key = await self.get_cache_key(email)

        await self.cache.set(cache_key, code, expire_time=self.code_expiry)

        template_body = {
            'company': f"{Values.COMPANY_NAME}",
            'd1': digits_dict['d6'],
            'd2': digits_dict['d5'],
            'd3': digits_dict['d4'],
            'd4': digits_dict['d3'],
            'd5': digits_dict['d2'],
            'd6': digits_dict['d1'],
            'minutes': Values.PASSWORD_TOKEN_EXPIRE_MINUTES
        }
        background_tasks.add_task(send_email,
                                  subject="درخواست بازیابی رمز عبور",
                                  recipients=[user.Email],
                                  template_name="forget-password.html",
                                  template_body=template_body,
                                  sender_name="Company-name",
                                  sender_email="rescue@Hooshinai.com",
                                  html=True
                                  )

        return {"message": "کد بازیابی رمز عبور به ایمیل شما ارسال شد"}

    async def send_reset_code_phone(self, phone_number: str, background_tasks: BackgroundTasks) -> dict:
        user = await self.get_user_by_phone(phone_number)
        if not user:
            raise HTTPException(status_code=404, detail="اطلاعات وارد شده وجود ندارد یا اشتباه است.")

        await self.verify_local_user(user)

        code = await self.generate_verification_code()
        cache_key = await self.get_cache_key(phone_number)

        await self.cache.set(cache_key, code, expire_time=self.code_expiry)

        background_tasks.add_task(self.sms_controller.send_forget_password_code,
                                  mobile=phone_number,
                                  code=int(code),
                                  user_name=user.FirstName
                                  )

        return {"detail": "کد بازیابی رمز عبور به تلفن شما ارسال شد"}

    async def verify_and_reset_password(
            self,
            code: str,
            new_password: str,
            background_tasks: BackgroundTasks,
            email: Optional[str] = None,
            phone_number: Optional[str] = None
    ) -> dict:
        if not (email or phone_number):
            raise HTTPException(
                status_code=400,
                detail="ایمیل یا شماره تلفن باید ارائه شود"
            )

        identifier = email or phone_number
        cache_key = await self.get_cache_key(identifier)

        stored_code = int(await self.cache.get(cache_key))
        if not stored_code or stored_code != int(code):
            raise HTTPException(
                status_code=400,
                detail="کد تأیید نامعتبر یا منقضی شده است"
            )

        async with get_db_outside() as db:
            from sqlalchemy import update

            new_hashed_password, salt = self.password_service.get_password_hash(new_password)

            # Direct update statement
            stmt = (
                update(User)
                .where(User.Email == email if email else User.PhoneNumber == phone_number)
                .values(Password=new_hashed_password, Salt=salt.decode('utf-8'))
                .returning(User.id)
            )

            result = await db.execute(stmt)
            updated_user_id = result.scalar_one_or_none()

            if not updated_user_id:
                raise HTTPException(status_code=404, detail="اطلاعات کاربری اشتباه یا وجود ندارد.")

            await db.commit()

        await self.cache.delete(cache_key)
        return {"message": "Password successfully reset"}
