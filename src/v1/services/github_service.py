from fastapi import HTTPException
from starlette import status
import aiohttp
from configurations.OAuth import OAuthService
from src.v1.utils import download_and_convert_to_base64


class GitHubService:
    def __init__(self, oauth_service: OAuthService):
        self.oauth_service = oauth_service

    async def get_login_url(self):
        """Generate GitHub OAuth URL"""
        auth_url = (
            "https://github.com/login/oauth/authorize"
            f"?client_id={self.oauth_service.config.GITHUB_CLIENT_ID}"
            f"&redirect_uri={self.oauth_service.config.GITHUB_REDIRECT_URI}"
            "&scope=user:email"
        )
        return {"url": auth_url}

    async def handle_callback(self, code: str):
        """Process GitHub callback and return user info"""
        try:
            # Get access token
            token_data = await self._get_access_token(code)
            access_token = token_data["access_token"]

            # Get user data and email
            async with aiohttp.ClientSession() as session:
                user_data = await self._get_github_user(session, access_token)
                primary_email = await self._get_github_email(session, access_token)

            # Convert avatar to base64
            profile_image = await download_and_convert_to_base64(user_data.get("avatar_url"))

            return {
                "email": primary_email,
                "github_id": str(user_data["id"]),
                "access_token": access_token,
                "name": user_data.get("name", ""),
                "profile_image": profile_image
            }

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"GitHub authentication failed: {str(e)}"
            )

    async def _get_access_token(self, code: str) -> dict:
        """Exchange code for access token"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    "https://github.com/login/oauth/access_token",
                    headers={"Accept": "application/json"},
                    json={
                        "client_id": self.oauth_service.config.GITHUB_CLIENT_ID,
                        "client_secret": self.oauth_service.config.GITHUB_CLIENT_SECRET,
                        "code": code,
                    }
            ) as response:
                token_data = await response.json()
                if "error" in token_data:
                    raise ValueError(f"GitHub OAuth error: {token_data['error']}")
                return token_data

    async def _get_github_user(self, session: aiohttp.ClientSession, access_token: str) -> dict:
        """Get GitHub user data"""
        async with session.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json"
                }
        ) as response:
            if response.status != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="خطا در دریافت اطلاعات از گیت هاب؛ لطفا اتصال خود را چک کنید"
                )
            return await response.json()

    async def _get_github_email(self, session: aiohttp.ClientSession, access_token: str) -> str:
        """Get GitHub user's primary email"""
        async with session.get(
                "https://api.github.com/user/emails",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json"
                }
        ) as response:
            if response.status != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to fetch GitHub emails"
                )

            emails = await response.json()
            primary_email = next(
                (email["email"] for email in emails if email["primary"]),
                emails[0]["email"] if emails else None
            )
            if not primary_email:
                raise ValueError("No email found in GitHub account")
            return primary_email