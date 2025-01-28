# src/v1/auth/services/auth/magic_link_service.py

from datetime import datetime, timedelta
import jwt
from fastapi import HTTPException
from sqlalchemy import select
from starlette import status

from configurations.db_config import get_db_outside
from configurations.environments import Values
from src.v1.models.user import User
from src.v1.services.email_service import send_email


class MagicLinkService:
    @staticmethod
    def __token_time_calculate() -> int:
        expiration_time = datetime.now() + timedelta(minutes=int(Values.EMAIL_TOKEN_EXPIRE_MINUTES))
        return int(expiration_time.timestamp())

    def __produce_magic_link_email_token(self, user_uuid: str):
        print('here 5')
        token = jwt.encode(payload={
            'sub': user_uuid,
            'exp': self.__token_time_calculate(),
            'iat': int(datetime.now().timestamp()),
            'type': 'magic_link'
        }, key=Values.JWT_EMAIL_SECRET_KEY, algorithm=Values.ALGORITHM)
        print('here 6')
        return token

    async def produce_magic_link(self, user):
        print('here 7')
        print(user)
        if user.Email:
            print('here4')
            token = self.__produce_magic_link_email_token(str(user.uuid))
            print('here 2')
            return f'{Values.BASE_URL}/{Values.MAGIC_LINK_CALLBACK}?magic={token}'
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='اطلاعات اشتباه یا موجود نمی باشد'
            )

    async def send_magic_link(self, user):
        link = await self.produce_magic_link(user)
        r = await send_email(
            subject="لینک ورود",
            recipients=[user.Email],
            template_name="magic-link.html",
            template_body={"link": link, 'company': f"{Values.COMPANY_NAME}"},
            sender_name="Company-name",
            sender_email="login@mail.hooshinai.com",
            html=True
        )
        print(r)

    @staticmethod
    async def verify_magic_link(token: str) -> User:
        # try:
        decoded_token = jwt.decode(token, Values.JWT_EMAIL_SECRET_KEY, algorithms=Values.ALGORITHM)
        print(decoded_token)
        async with get_db_outside() as db:
            user = await db.scalar(select(User).where(User.uuid == decoded_token['sub']))
            if user:
                return user
            else:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                    detail='اطلاعات اشتباه یا موجود نمی باشد')
