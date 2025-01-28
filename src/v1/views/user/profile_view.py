from fastapi import Depends
from configurations.cbv import cbv
from configurations.router import SlashInferringRouter
from src.v1.middlewares.auth_dependency import get_current_user
from src.v1.models.user import User, UserPermission
from src.v1.schemas.profile_schema import UserMinimalDisplay, UserPermissionListDisplay, UpdateUserInfoSchema, \
    UserContactInfoDisplaySchema
from src.v1.services.profile_info_service import ProfileInfoService

user_profile_router = SlashInferringRouter(prefix="/api/v1/user", tags=["Profile Management"])


@cbv(user_profile_router)
class UserProfileView:
    current_user: User = Depends(get_current_user)
    profile_service = ProfileInfoService()

    @user_profile_router.get('/get-info', response_model=UserMinimalDisplay)
    async def get_user_info(self):
        return await self.profile_service.get_user_info(self.current_user)

    @user_profile_router.patch('/edit', response_model=UserMinimalDisplay)
    async def edit_user_info(self, in_data: UpdateUserInfoSchema):
        return await self.profile_service.update_user_info(in_data, self.current_user.uuid)

    @user_profile_router.get('/permission', response_model=UserPermissionListDisplay)
    async def get_user_permission(self):
        return await self.profile_service.get_user_permissions(self.current_user)

    @user_profile_router.get('/get/contact-info',response_model=UserContactInfoDisplaySchema)
    async def get_user_contact_info(self):
        return await self.profile_service.get_user_contact_info(self.current_user)