# src/v1/auth/views/register/local_individual_register.py

from fastapi import BackgroundTasks, HTTPException
from starlette import status
from starlette.responses import Response
from configurations.cbv import cbv
from configurations.router import SlashInferringRouter
from src.v1.schemas.auth_schema import UserCreateSchema, VerifyLinkEmailSchema, TokenDisplay
from src.v1.schemas.register_schema import ResponseSchema
from src.v1.services.cookie_service import set_auth_cookie
from src.v1.services.register_service import RegisterService
from src.v1.services.base_auth_service import AuthService

router = SlashInferringRouter(prefix="/api/v1/register", tags=['local register'])


@cbv(router)
class RegisterView:
    background_tasks: BackgroundTasks
    register_service = RegisterService()
    auth_service = AuthService()

    @router.post('/s1', response_model=ResponseSchema)
    async def register_user_step_1(self, in_user: UserCreateSchema):
        """Handle step 1 of user registration"""
        try:
            # Add email sending to background tasks
            self.background_tasks.add_task(self.register_service.create_user_step1,
                                           email=str(in_user.Email),
                                           password=in_user.Password
                                           )

            return ResponseSchema(
                status_code=status.HTTP_201_CREATED,
                detail="ایمیل تایید ارسال شد",
            )
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    @router.post('/s2')
    async def register_user_step_2(self, response: Response, in_token: VerifyLinkEmailSchema):
        """Handle step 2 of user registration"""
        try:
            # Create user
            new_user = await self.register_service.create_user_step2(in_token.Token)

            # Generate tokens
            access_token = await self.auth_service.token_service.create_access_token(
                str(new_user.uuid)
            )
            refresh_token = await self.auth_service.token_service.create_refresh_token(
                str(new_user.uuid)
            )

            # Set cookie
            await set_auth_cookie(
                response,
                access_token,
                refresh_token
            )

            return TokenDisplay(
                AccessToken=access_token,
                RefreshToken=refresh_token,
                TokenType='bearer'
            )

        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
