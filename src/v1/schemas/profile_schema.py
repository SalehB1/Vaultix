# src/v1/auth/schemas/profile_schema.py
import re
from enum import Enum
from typing import Optional, Any, List
from uuid import UUID

from pydantic import BaseModel, EmailStr, field_validator, model_validator, Field

from src.v1.models.user import UserTypes, AuthProvider, User


class SignUpType(Enum):
    github = "GI"
    google = "GO"


class ProfileResponse(BaseModel):
    detail: str
    Email: Optional[str] = None
    PhoneNumber: Optional[str] = None

    class Config:
        from_attributes = True


class UserMinimalDisplay(BaseModel):
    Name: str | None  # This will show FirstName
    UserType: UserTypes
    AuthProvider: AuthProvider
    ProfileImage: str | None  # For base64 image
    VerifiedPhone: bool

    @model_validator(mode='before')
    def transform_fields(cls, values):
        # When using from_orm, values will be the User model instance
        if hasattr(values, 'FirstName'):
            # Create a new attribute 'Name' from FirstName
            setattr(values, 'Name', getattr(values, 'FirstName', ''))
        return values

    class Config:
        from_attributes = True


class UserPermissionByIdDisplay(BaseModel):
    uuid: UUID  # Only uuid field

    class Config:
        from_attributes = True


class UserPermissionListDisplay(BaseModel):
    UserPermission: List[UserPermissionByIdDisplay]  # List of permission UUIDs

    class Config:
        from_attributes = True


class SendUpdateEmailSchema(BaseModel):
    Email: EmailStr


class UpdateEmailSchema(BaseModel):
    Email: EmailStr
    NewEmail: EmailStr
    Code: str


class SendPhoneCodeSchema(BaseModel):
    PhoneNumber: str

    @field_validator('PhoneNumber')
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        # Remove any spaces or dashes
        v = re.sub(r'[\s-]', '', v)

        # Pattern for Iranian phone numbers
        # Matches: 09123456789, +989123456789, 00989123456789
        pattern = r'^(?:(?:\+98|0098|0)?9\d{9})$'

        if not re.match(pattern, v):
            raise ValueError('فرمت شماره معتبر نیست')

        # Convert all formats to standard 09XXXXXXXXX format
        if v.startswith('+98'):
            v = '0' + v[3:]
        elif v.startswith('0098'):
            v = '0' + v[4:]

        return v


class UpdatePhoneSchema(BaseModel):
    PhoneNumber: str
    Code: str

    @field_validator('PhoneNumber')
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        # Remove any spaces or dashes
        v = re.sub(r'[\s-]', '', v)

        pattern = r'^(?:(?:\+98|0098|0)?9\d{9})$'

        if not re.match(pattern, v):
            raise ValueError('فرمت شماره معتبر نیست')

        if v.startswith('+98'):
            v = '0' + v[3:]
        elif v.startswith('0098'):
            v = '0' + v[4:]

        return v


class UpdateUserInfoSchema(BaseModel):
    Name: Optional[str] = None
    ProfileImage: Optional[str] = None


class UserContactInfoDisplaySchema(BaseModel):
    Email: str
    PhoneNumber: str | None
