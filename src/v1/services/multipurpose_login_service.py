# src/v1/auth/services/auth/multipurpose_login_service.py
import random
import re
from datetime import datetime, timedelta
from typing import Any, Dict

import jwt
from fastapi import HTTPException
from starlette import status
from sqlalchemy import select
from configurations.cache import Cache
from configurations.db_config import get_db_outside
from configurations.environments import Values
from src.v1.models.user import User
from src.v1.services.email_service import send_email
from src.v1.services.otp_service import Otp
from src.v1.services.password_service import PasswordService


class MultiPurposeLoginService:
    def __init__(self):
        self.cache = Cache()
        self.sms_controller = Otp()
        self.password_service = PasswordService()

    @staticmethod
    def validate_identifier(identifier):
        if not identifier:
            raise ValueError('Identifier cannot be empty')

        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if re.match(email_regex, identifier):
            return 'email'

        phone_regex = r'^\d+$'
        if re.match(phone_regex, identifier):
            return 'phone'

        return 'username'

    async def __check_otp_code(self, phone_number, in_code):
        saved_code = await self.cache.get(f'otp-phone-{phone_number}')
        return saved_code == int(in_code)

    async def login_with_phone(self, phone_number: str, code: str) -> User:

        async with get_db_outside() as db:
            user = await db.scalar(
                select(User).where(User.PhoneNumber == phone_number, User.IsActive == True, User.is_deleted == False))
            if not user:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='اطلاعات اشتباه یا موجود نمی باشد')
            if not await self.__check_otp_code(phone_number, code):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='اطلاعات اشتباه یا موجود نمی باشد')
            else:
                return user

    async def __produce_code(self, mobile):
        code = random.randint(100000, 999999)
        await self.cache.set(f'otp-phone-{mobile}', code, expire_time=timedelta(minutes=Values.OTP_EXPIRE_TIME_MINUTES))
        return code

    async def login(self, username: str, password: str):
        identifier_type = self.validate_identifier(username)
        with get_db_outside() as db:
            if identifier_type == 'email':
                user = await db.scalar(select(User).where(User.Email == username))
            elif identifier_type == 'phone':
                user = await db.scalar(select(User).where(User.PhoneNumber == username))
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail='اطلاعات اشتباه یا موجود نمی باشد'
                )
            if not self.password_service.verify_password(password, user.Password, user.Salt):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail='اطلاعات اشتباه یا موجود نمی باشد'
                )
            return user

    @staticmethod
    async def get_user_by_email(email: str) -> Any | None:
        async with get_db_outside() as db:
            user = await db.scalar(
                select(User).where(User.Email == email, User.is_deleted == False, User.IsActive == True))
        if user:
            return user
        else:
            return None

    @staticmethod
    async def get_user_by_email_for_magic_link(email: str) -> Any | None:
        async with get_db_outside() as db:
            user = await db.scalar(
                select(User).where(User.Email == email, User.is_deleted == False, User.IsActive == True,
                                   ))
        if user:
            if user.is_local_user:
                return user
        else:
            return None

    @staticmethod
    def __token_time_calculate() -> int:
        expiration_time = datetime.now() + timedelta(minutes=int(Values.EMAIL_TOKEN_EXPIRE_MINUTES))
        return int(expiration_time.timestamp())

    async def __produce_verify_email_token(self, user_email: str):
        print('starting create token')
        token = jwt.encode(payload={
            'sub': user_email,
            'exp': self.__token_time_calculate(),
            'iat': int(datetime.now().timestamp()),  # Convert to Unix timestamp
            'type': 'verify_email'
        }, key=Values.JWT_EMAIL_SECRET_KEY, algorithm=Values.ALGORITHM)
        print(token)
        return token

    async def produce_verify_email_link(self, user_email):
        print('produce email link start')
        token = await self.__produce_verify_email_token(user_email)
        verify_url_path = f'{Values.BASE_URL}/{Values.VERIFY_EMAIL_CALLBACK}?token={token}'
        print('produce link',verify_url_path)
        return verify_url_path

    async def send_verify_email(self, email: str):

        print('enter verify')
        link = await self.produce_verify_email_link(email)
        print('start sending email')
        result = await send_email(
            subject="خوش آمدید | تایید ایمیل",
            recipients=[email],
            template_name="welcome.html",
            template_body={"link": link, 'company': f"{Values.COMPANY_NAME}"},
            sender_name="Company-name",
            sender_email="welcome@mail.hooshinai.com",
            html=True
        )
        print('the result for send email', result)

    async def extract_user_from_email_token(self, token) -> Dict:
        try:
            user_data = jwt.decode(token, Values.JWT_EMAIL_SECRET_KEY, algorithms=[Values.ALGORITHM])

            if user_data.get('sub', None):
                return await self.cache.get(f'new_user:{user_data["sub"]}')

        except Exception as e:
            print(e)

    async def get_user_by_phone(self, phone_number: str):
        try:
            async with get_db_outside() as db:
                check_user = await db.scalar(select(User).where(User.PhoneNumber == phone_number))
            if check_user:
                return check_user
            else:
                return None
        except Exception as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED,
                                detail='خطا در پردازش لطفا مجددا تلاش کنید')

    async def send_otp_code_phone(self, in_mobile: str):
        produced_code = await self.__produce_code(mobile=in_mobile)
        send_status = await self.sms_controller.send__login_code(mobile=in_mobile, code=produced_code)
        print(produced_code, send_status)
        if send_status:
            return True
        else:
            await self.send_otp_code_phone(in_mobile)

    async def login_with_email(self, email: str, password: str):
        print('in-login')
        async with get_db_outside() as db:
            user = await db.scalar(select(User).where(User.Email == email))
            if user:
                print('user ro darim',user.is_local_user)
                if not user.is_local_user:
                    print('in here')
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                        detail='اطلاعات اشتباه یا موجود نمی باشد')

            if not user:
                print('no way here?')
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='اطلاعات اشتباه یا موجود نمی باشد')
            if not self.password_service.verify_password(plain_password=password, hashed_password=user.Password,
                                                         salt=user.Salt):
                print('inja miam')
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='اطلاعات اشتباه یا موجود نمی باشد')
            else:
                print('inja nemin')
                return user
