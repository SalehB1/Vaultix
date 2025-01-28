import re

from pydantic import BaseModel, field_validator, EmailStr
from typing import Optional

from src.v1.models.user import AuthProvider


class UserCreateSchema(BaseModel):
    Email: EmailStr
    Password: str

    @field_validator('Password')
    @classmethod
    def validate_password(cls, password: str) -> str:
        if not re.search(r'[A-Z]', password):
            raise ValueError('رمز عبور باید حداقل یک حرف بزرگ داشته باشد')

        if not re.search(r'\d', password):
            raise ValueError('رمز عبور باید حداقل یک عدد داشته باشد')

        return password


class MagicLinkEmailLoginSchema(BaseModel):
    Email: EmailStr


class VerifyLinkEmailSchema(BaseModel):
    Token: str


class MagicLinkEmailVerifySchema(BaseModel):
    Token: str


class EmailPassLoginSchema(BaseModel):
    Email: EmailStr
    Password: str


class PhoneOtpLoginDisplaySchema(BaseModel):
    detail: str


class SendOtpSchema(BaseModel):
    PhoneNumber: str
    Realm: str

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


class VerifyOtpSchema(BaseModel):
    PhoneNumber: str
    Code: str

    @field_validator('PhoneNumber')
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        # Remove any spaces or dashes
        v = re.sub(r'[\s-]', '', v)

        # Pattern for Iranian phone numbers
        # Matches: 09123456789, +989123456789, 00989123456789
        pattern = r'^(?:(?:\+98|0098|0)?9\d{9})$'

        if not re.match(pattern, v):
            raise ValueError('Invalid Iranian phone number format')

        # Convert all formats to standard 09XXXXXXXXX format
        if v.startswith('+98'):
            v = '0' + v[3:]
        elif v.startswith('0098'):
            v = '0' + v[4:]

        return v

    @field_validator('Code')
    @classmethod
    def validate_code(cls, v: str) -> str:
        # Remove any non-digit characters
        cleaned_code = re.sub(r'\D', '', v)

        # Check if code is exactly 6 digits
        if not re.match(r'^\d{6}$', cleaned_code):
            raise ValueError("Code must be exactly 6 digits")

        return cleaned_code


class TokenDisplay(BaseModel):
    AccessToken: str
    RefreshToken: str
    TokenType: Optional[str] = 'bearer'


class RefreshToken(BaseModel):
    refresh_token: str


class OAuthUserData(BaseModel):
    email: str
    first_name: str
    last_name: str
    provider_id: str
    provider: AuthProvider
    access_token: str
    phone_number: Optional[str] = None

class OAuthURLResponse(BaseModel):
    url: str



class LogoutDisplaySchema(BaseModel):
    detail: str