from fastapi import HTTPException
from starlette import status
import aiohttp
from configurations.OAuth import OAuthService
from src.v1.utils import download_and_convert_to_base64
import logging
from urllib.parse import quote, unquote

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleService:
    def __init__(self, oauth_service: OAuthService):
        self.oauth_service = oauth_service

    async def get_login_url(self):
        """Generate Google OAuth URL"""
        scopes = [
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
            "openid"
        ]

        encoded_scopes = quote(' '.join(scopes))

        auth_url = (
            "https://accounts.google.com/o/oauth2/v2/auth"
            f"?client_id={quote(self.oauth_service.config.GOOGLE_CLIENT_ID)}"
            f"&redirect_uri={quote(self.oauth_service.config.GOOGLE_REDIRECT_URI)}"
            "&response_type=code"
            f"&scope={encoded_scopes}"
            "&access_type=offline"
            "&prompt=consent"
            "&include_granted_scopes=true"
        )
        return {"url": auth_url}

    async def handle_callback(self, code: str):
        """Process Google callback and return user info"""
        try:
            decoded_code = unquote(code)
            logger.info(f"Processing callback with decoded code length: {len(decoded_code)}")

            async with aiohttp.ClientSession() as session:
                # Get access token
                token_data = await self._get_access_token(decoded_code, session)
                access_token = token_data["access_token"]
                logger.info("Successfully obtained access token")

                # Get user data
                user_data = await self._get_google_user(access_token, session)
                logger.info("Successfully obtained user data")

                # Convert profile picture to base64
                profile_image = await download_and_convert_to_base64(user_data.get("picture"))
                logger.info("Successfully processed profile image")

                return {
                    "email": user_data.get("email"),
                    "google_id": user_data.get("sub"),
                    "access_token": access_token,
                    "name": user_data.get("name", ""),
                    "profile_image": profile_image
                }

        except HTTPException as e:
            logger.error(f"HTTP error during callback: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in callback: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Google authentication failed: {str(e)}"
            )

    async def _get_access_token(self, code: str, session: aiohttp.ClientSession) -> dict:
        """Exchange code for access token"""
        token_url = "https://oauth2.googleapis.com/token"

        data = {
            "client_id": self.oauth_service.config.GOOGLE_CLIENT_ID,
            "client_secret": self.oauth_service.config.GOOGLE_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.oauth_service.config.GOOGLE_REDIRECT_URI
        }

        try:
            async with session.post(token_url, data=data) as response:
                response_data = await response.json()
                if response.status != 200:
                    error_msg = response_data.get('error_description', '') or response_data.get('error', '')
                    logger.error(f"Token exchange failed: {error_msg}")
                    logger.debug(f"Response data: {response_data}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Failed to get Google access token: {error_msg}"
                    )
                return response_data
        except aiohttp.ClientError as e:
            logger.error(f"Network error during token exchange: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to communicate with Google: {str(e)}"
            )

    async def _get_google_user(self, access_token: str, session: aiohttp.ClientSession) -> dict:
        """Get Google user data"""
        userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"

        try:
            async with session.get(
                    userinfo_url,
                    headers={"Authorization": f"Bearer {access_token}"}
            ) as response:
                response_data = await response.json()
                if response.status != 200:
                    error_msg = response_data.get('error_description', '') or response_data.get('error', '')
                    logger.error(f"User info fetch failed: {error_msg}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Failed to fetch Google user data: {error_msg}"
                    )
                return response_data
        except aiohttp.ClientError as e:
            logger.error(f"Network error fetching user data: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to communicate with Google: {str(e)}"
            )