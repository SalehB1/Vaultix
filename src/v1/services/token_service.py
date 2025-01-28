# src/v1/auth/services/auth/token_service.py

from datetime import datetime, timedelta
from typing import Union, Any
import jwt
from fastapi import Response, HTTPException
from jwt import InvalidTokenError, DecodeError, ExpiredSignatureError
import json
from sqlalchemy import select
import sqlalchemy
from starlette import status

from configurations.db_config import get_db_outside
from configurations.environments import Values
from src.v1.models.user import User


class TokenService:
    def __init__(self):
        self.access_token_expire = Values.ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire = Values.REFRESH_TOKEN_EXPIRE_MINUTES
        self.algorithm = Values.ALGORITHM
        self.jwt_secret = Values.JWT_SECRET_KEY
        self.jwt_refresh_secret = Values.JWT_REFRESH_SECRET_KEY

    async def create_access_token(self, subject: Union[str, Any], expires_delta: int = None) -> str:
        expires = self._calculate_expiry(expires_delta or self.access_token_expire)
        to_encode = {"exp": expires, "sub": str(subject)}
        return jwt.encode(to_encode, self.jwt_secret, self.algorithm)

    async def create_refresh_token(self, subject: Union[str, Any], expires_delta: int = None) -> str:
        expires = self._calculate_expiry(expires_delta or self.refresh_token_expire)
        to_encode = {"exp": expires, "sub": str(subject)}
        return jwt.encode(to_encode, self.jwt_refresh_secret, self.algorithm)

    @staticmethod
    def _calculate_expiry(expires_delta: int) -> datetime:
        return datetime.utcnow() + timedelta(minutes=expires_delta)

    async def verify_token(self, token: str, db) -> User:
        """Verify access token and return user"""
        return await self.__check_token(self.jwt_secret, token, db)

    async def verify_refresh_token(self, token: str, db) -> User:
        """Verify refresh token and return user"""
        return await self.__check_token(self.jwt_refresh_secret, token, db, refresh=True)

    async def __check_token(self, secret: str, token: str, db, refresh: bool = False) -> User:
        try:
            payload = jwt.decode(token, secret, algorithms=[self.algorithm])
            user = await db.scalar(select(User).where(User.uuid == payload.get('sub')))
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail='اطلاعات نامعتبر است؛ لطفا مجدد وارد شوید'
                )
            if not user.IsActive:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail='کاربر غیرفعال است'
                )
            return user
        except sqlalchemy.orm.exc.NoResultFound:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='اطلاعات نامعتبر است؛ لطفا مجدد وارد شوید'
            )
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='ورود منقضی شده است؛ لطفا مجدد وارد شوید'
            )
        except (DecodeError, InvalidTokenError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='اطلاعات نامعتبر است؛ لطفا مجدد وارد شوید'
            )

    @staticmethod
    async def extract_tokens_from_cookie(raw_token):
        try:
            tokens = json.loads(raw_token)
            tokens['refresh_token'] = tokens['refresh_token'].split(' ')[1]
            tokens['access_token'] = tokens['access_token'].split(' ')[0]
            print(tokens)
            return tokens
        except json.decoder.JSONDecodeError:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail='خطا در مقادیر دریافتی ؛ لطفا مجددا وارد شوید')

    async def create_token_from_refresh(self, request):
        cookie_tokens = request.cookies.get(Values.COOKIE_NAME)
        if not cookie_tokens:
            raise HTTPException(status_code=status.HTTP_410_GONE, detail="لطفا مجددا وارد  شوید")
        tokens = await self.extract_tokens_from_cookie(cookie_tokens)
        async with get_db_outside() as db:
            user = await self.verify_refresh_token(tokens['refresh_token'], db)
        return user