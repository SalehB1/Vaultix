# src/v1/auth/services/auth/register_service.py

from fastapi import HTTPException
from starlette import status
from sqlalchemy import select
from configurations.cache import Cache
from configurations.db_config import get_db_outside
from src.v1.models.user import User, UserTypes
from src.v1.services.base_auth_service import AuthService
from src.v1.services.multipurpose_login_service import MultiPurposeLoginService
import uuid


class RegisterService:
    def __init__(self):
        self.cache = Cache()
        self.auth_service = AuthService()
        self.multipurpose_login = MultiPurposeLoginService()

    async def create_user_step1(self, email: str, password: str):
        async with get_db_outside() as db:
            exist_user = await db.scalar(select(User).where(User.Email == email))
            if exist_user:
                raise HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE,
                    detail='ثبت نام با این ایمیل ممکن نیست!'
                )

        # Hash password and prepare user data
        hashed_password, salt = self.auth_service.password_service.get_password_hash(password=password)
        new_user = {
            "Email": str(email).lower().strip(),
            "Password": hashed_password,
            "Salt": salt.decode('utf-8'),
            "UserType": UserTypes.individual
        }

        # Save to cache
        await self.cache.set(key=f'new_user:{email}', value=new_user)

        # Send verification email
        await self.multipurpose_login.send_verify_email(str(email))

        return email

    async def create_user_step2(self, token: str):
        """Handle second step of user registration"""
        # Get user data from token
        user_data = await self.multipurpose_login.extract_user_from_email_token(token=token)
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Token invalid or expired'
            )

        async with get_db_outside() as db:
            # Check if user exists
            exist_user = await db.scalar(select(User).where(User.Email == user_data['Email']))
            if exist_user:
                raise HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE,
                    detail='ثبت نام با این ایمیل ممکن نیست!'
                )

            try:
                # Create new user
                new_user = User(
                    Email=user_data['Email'],
                    PhoneNumber=str(uuid.uuid4())[:11],
                    Password=user_data['Password'],
                    Salt=str(user_data["Salt"]),
                    UserType=user_data["UserType"]
                )

                db.add(new_user)
                await db.commit()
                await db.refresh(new_user)
                return new_user

            except Exception as e:
                await db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail='مشکلی در ثبت نام به وجود‌آمد ، لطفا دوباره شروع کنید'
                )