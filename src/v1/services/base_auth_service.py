from src.v1.services.magic_link_service import MagicLinkService
from src.v1.services.multipurpose_login_service import MultiPurposeLoginService
from src.v1.services.password_service import PasswordService
from src.v1.services.token_service import TokenService


class AuthService:
    def __init__(self):
        self.token_service = TokenService()
        self.password_service = PasswordService()
        self.magic_link_service = MagicLinkService()
        self.multipurpose_login = MultiPurposeLoginService()

    # Add convenience methods here to access the most commonly used methods
    async def authenticate_user(self, username: str, password: str):
        return await self.multipurpose_login.login(username, password)

    async def create_tokens(self, user_id: str):
        access_token = await self.token_service.create_access_token(user_id)
        refresh_token = await self.token_service.create_refresh_token(user_id)
        return access_token, refresh_token