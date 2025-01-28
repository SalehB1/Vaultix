# src/v1/auth/middlewares/auth_dependency.py

from fastapi import Depends, HTTPException, Request
from starlette import status
from configurations.OAuth import OAuth2PasswordBearerWithCookie
from configurations.db_config import get_db_outside
from src.v1.services.token_service import TokenService

oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/api/v1/auth/email")
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        token_service = TokenService()


        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="لطفا وارد پرتال شوید"
            )

        # Verify token and get user
        async with get_db_outside() as db:
            user = await token_service.verify_token(token, db)
            return user

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="لطفا مجدداً وارد سیستم شوید"
        )