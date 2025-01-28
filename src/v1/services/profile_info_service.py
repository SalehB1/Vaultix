import re

from sqlalchemy import select
from configurations.db_config import get_db_outside
from src.v1.models.user import User
from src.v1.schemas.profile_schema import UserPermissionListDisplay, UserPermissionByIdDisplay, UserMinimalDisplay


class ProfileInfoService:
    @staticmethod
    def __phone_number_checker(phone_number) -> bool:
        v = re.sub(r'[\s-]', '', phone_number)

        # Pattern for Iranian phone numbers
        # Matches: 09123456789, +989123456789, 00989123456789
        pattern = r'^(?:(?:\+98|0098|0)?9\d{9})$'

        if not re.match(pattern, v):
            return False
        else:
            return True

    async def get_user_info(self, current_user: User):
        return UserMinimalDisplay(Name=current_user.FirstName, UserType=current_user.UserType,
                                  AuthProvider=current_user.AuthProvider, ProfileImage=current_user.ProfileImage,
                                  VerifiedPhone=self.__phone_number_checker(current_user.PhoneNumber))

    @staticmethod
    async def get_user_permissions( current_user: User):
        # Convert permissions to UUID-only format
        permission_list = [
            UserPermissionByIdDisplay(uuid=perm.id)
            for perm in current_user.CustomPermissions
        ]
        return UserPermissionListDisplay(UserPermission=permission_list)


    async def update_user_info(self,in_data, current_user_id: User) -> User:
        async with get_db_outside() as db:
            user = await db.scalar(select(User).where(User.uuid == current_user_id))
            if in_data.Name:
                user.FirstName = in_data.Name
            if in_data.ProfileImage:
                user.ProfileImage = in_data.ProfileImage

            await db.commit()
        return UserMinimalDisplay(Name=user.FirstName, UserType=user.UserType,
                                  AuthProvider=user.AuthProvider, ProfileImage=user.ProfileImage,
                                  VerifiedPhone=self.__phone_number_checker(user.PhoneNumber))

    @staticmethod
    async def get_user_contact_info(current_user):

        return current_user
