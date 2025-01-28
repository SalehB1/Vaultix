from enum import Enum

from sqlalchemy import Column, String, Integer, Boolean, Text, Enum as SQLAlchemyEnum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from configurations.db_config import DbBaseModel


class AuthProvider(str, Enum):
    LOCAL = "local"
    GOOGLE = "google"
    GITHUB = "github"


class NotificationMethod(Enum):
    email = 'email'
    sms = 'sms'
    email_sms = 'email_sms'


class UserTypes(Enum):
    individual = 'individual'
    corporate = 'corporate'


class User(DbBaseModel):
    __tablename__ = "users"
    FirstName = Column(String(50), nullable=True)
    LastName = Column(String(50), nullable=True)
    Email = Column(String(50), nullable=False, unique=True)
    PhoneNumber = Column(String(12), nullable=False, unique=True)
    IsActive = Column(Boolean, default=True)
    Salt = Column(String(50), nullable=True)
    Password = Column(String(200), nullable=True)
    ProfileImage= Column(Text, nullable=True)
    UserType = Column(SQLAlchemyEnum(UserTypes), nullable=False)
    RoleId = Column(Integer, ForeignKey("roles.id"), nullable=True)
    CustomPermissions = relationship("Permission", secondary="user_permissions", back_populates="Users",
                                     lazy='subquery', uselist=True)
    Role = relationship("Role", back_populates="Users", lazy='subquery', uselist=False)
    NotificationMethod = Column(SQLAlchemyEnum(NotificationMethod), nullable=False,
                                default=NotificationMethod.email_sms)
    AuthProvider = Column(SQLAlchemyEnum(AuthProvider), default=AuthProvider.LOCAL)
    GoogleId = Column(String, unique=True, nullable=True)
    GoogleAccessToken = Column(String, nullable=True)
    GithubId = Column(String, unique=True, nullable=True)
    GithubAccessToken = Column(String, nullable=True)

    @property
    def is_oauth_user(self):
        return self.AuthProvider != AuthProvider.LOCAL

    @property
    def is_local_user(self):
        return self.AuthProvider == AuthProvider.LOCAL

    def update_oauth_info(self, provider: AuthProvider, provider_id: str, access_token: str):
        self.AuthProvider = provider
        if provider == AuthProvider.GOOGLE:
            self.GoogleId = provider_id
            self.GoogleAccessToken = access_token
        elif provider == AuthProvider.GITHUB:
            self.GithubId = provider_id
            self.GithubAccessToken = access_token



class Role(DbBaseModel):
    __tablename__ = "roles"
    name = Column(String(30), unique=True)
    Users = relationship("User", back_populates="Role", lazy='subquery', uselist=True)
    Permissions = relationship("Permission", secondary="role_permissions", back_populates="Roles")


class Permission(DbBaseModel):
    __tablename__ = "permissions"
    Pname = Column(String(50), unique=False)
    Ename = Column(String(50), unique=False)
    Title = Column(String(50), unique=True)
    Roles = relationship("Role", secondary="role_permissions", back_populates="Permissions")
    Users = relationship("User", secondary="user_permissions", back_populates="CustomPermissions", lazy='subquery',
                         uselist=True)

    def __repr__(self):
        return f"Permission(id={self.id}, Pname='{self.Pname}', Ename='{self.Ename}', Title='{self.Title}')"


class RolePermission(DbBaseModel):
    __tablename__ = "role_permissions"
    RoleId = Column(Integer, ForeignKey("roles.id"))
    PermissionId = Column(Integer, ForeignKey("permissions.id"))
    __table_args__ = (
        UniqueConstraint('PermissionId', 'RoleId', name='uq_role_permission'),
    )

    def __repr__(self):
        return f"RolePermission(id={self.id}, RoleId='{self.RoleId}', PermissionId='{self.PermissionId}')"


class UserPermission(DbBaseModel):
    __tablename__ = "user_permissions"
    UserId = Column(Integer, ForeignKey("users.id"))
    PermissionId = Column(Integer, ForeignKey("permissions.id"))
    __table_args__ = (
        UniqueConstraint('PermissionId', 'UserId', name='uq_user_permission'),

    )

    def __repr__(self):
        return f"UserPermission(id={self.id}, UserId='{self.UserId}', PermissionId='{self.PermissionId}')"
