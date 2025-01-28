import re

from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional


class RequestPasswordResetEmail(BaseModel):
    Email: EmailStr


class RequestPasswordResetPhone(BaseModel):
    PhoneNumber: str

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


class VerifyResetCode(BaseModel):
    Code: str
    Password: str
    Email: Optional[EmailStr] = None
    PhoneNumber: Optional[str] = None

    @field_validator('Password')
    @classmethod
    def validate_password(cls, password: str) -> str:
        if not re.search(r'[A-Z]', password):
            raise ValueError('رمز عبور باید حداقل یک حرف بزرگ داشته باشد')

        if not re.search(r'\d', password):
            raise ValueError('رمز عبور باید حداقل یک عدد داشته باشد')

        return password
