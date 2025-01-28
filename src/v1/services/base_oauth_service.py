# src/v1/auth/services/oauth/base_oauth_service.py
import uuid

from fastapi import HTTPException
from sqlalchemy import select
from starlette import status
from typing import Optional
from src.v1.models.user import User, AuthProvider, UserTypes, NotificationMethod
from src.v1.services.password_service import PasswordService
from configurations.db_config import get_db_outside


class BaseOAuthService:
    def __init__(self):
        self.password_service = PasswordService()

    async def handle_oauth_authentication(
            self,
            oauth_data: dict,
            provider: AuthProvider,
    ) -> User:
        """Handle OAuth authentication and return the user"""
        email = oauth_data.get('email')
        provider_id = oauth_data.get('google_id' if provider == AuthProvider.GOOGLE else 'github_id')
        access_token = oauth_data.get('access_token')
        name = oauth_data.get('name', '')
        profile_image = oauth_data.get('profile_image')

        if not email or not provider_id:
            raise HTTPException(
                status_code=400,
                detail=f"Incomplete user data received from {provider.value}"
            )

        # Check existing user
        user = await self._get_existing_user(email, provider, provider_id)

        if user:
            if user.AuthProvider == AuthProvider.LOCAL:
                raise HTTPException(
                    status_code=400,
                    detail="This email is already registered with password authentication"
                )
            return await self._update_oauth_user(user=user, provider=provider, provider_id=provider_id,
                                                 access_token=access_token, profile_image=profile_image)

        return await self._create_oauth_user(
            email, name, provider, provider_id, access_token, profile_image
        )

    @staticmethod
    async def _get_existing_user(email: str, provider: AuthProvider, provider_id: str) -> Optional[User]:
        async with get_db_outside() as db:
            provider_filter = (User.GoogleId == provider_id if provider == AuthProvider.GOOGLE
                               else User.GithubId == provider_id)
            stmt = select(User).where((User.Email == email) | provider_filter)
            result = await db.execute(stmt)
            return result.scalar_one_or_none()

    @staticmethod
    async def _update_oauth_user(
            user: User,
            provider: AuthProvider,
            provider_id: str,
            access_token: str,
            profile_image: Optional[str]
    ) -> User:
        async with get_db_outside() as db:
            user.update_oauth_info(provider, provider_id, access_token)
            if profile_image:
                user.ProfileImage = profile_image
            await db.commit()
            return user

    async def _create_oauth_user(
            self,
            email: str,
            name: str,
            provider: AuthProvider,
            provider_id: str,
            access_token: str,
            profile_image: Optional[str]
    ) -> User:
        try:
            async with get_db_outside() as db:
                # Split name into first and last name
                name_parts = name.split(' ', 1)
                first_name = name_parts[0]
                last_name = name_parts[1] if len(name_parts) > 1 else ""

                # Generate random password for OAuth users
                temp_password = await self.password_service.generate_password()
                password_hash, salt = self.password_service.get_password_hash(temp_password)

                user = User(
                    Email=email,
                    FirstName=first_name,
                    LastName=last_name,
                    PhoneNumber=str(uuid.uuid4())[:11],
                    UserType=UserTypes.individual,
                    AuthProvider=provider,
                    ProfileImage=profile_image,
                    NotificationMethod=NotificationMethod.email,
                    IsActive=True
                )

                user.update_oauth_info(provider, provider_id, access_token)

                db.add(user)
                await db.commit()
                await db.refresh(user)
                return user

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create user: {str(e)}"
            )
