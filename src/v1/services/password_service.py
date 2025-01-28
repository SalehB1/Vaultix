# src/v1/auth/services/auth/password_service.py

import bcrypt
import hashlib
import string
import random
from typing import Tuple

class PasswordService:
    @staticmethod
    def hash_password_with_salt(password: str, salt: bytes) -> bytes:
        return bcrypt.hashpw(password.encode('utf-8'), salt)

    @staticmethod
    def get_password_hash(password):
        salt = bcrypt.gensalt()
        password = password.encode('utf-8')
        salted_password = password + salt
        sha512_hash = hashlib.sha512()
        sha512_hash.update(salted_password)
        hashed_password = sha512_hash.hexdigest()
        return hashed_password, salt

    @staticmethod
    def get_hash_password_with_salt(password, salt):
        password = password.encode('utf-8')
        salt = salt.encode('utf-8')
        sha512_hash = hashlib.sha512()
        sha512_hash.update(password + salt)
        return sha512_hash.hexdigest()

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str, salt: str) -> bool:
        password = plain_password.encode('utf-8')
        salt = salt.encode('utf-8')
        sha512_hash = hashlib.sha512()
        sha512_hash.update(password + salt)
        hashed_string = sha512_hash.hexdigest()
        return hashed_string == hashed_password

    @staticmethod
    def hash_challenge_response(challenge: str, hashed_password: str) -> str:
        return hashlib.sha512((challenge + hashed_password).encode()).hexdigest()

    @staticmethod
    async def generate_password():
        characters = string.ascii_letters + string.digits + "!@#$%&*"
        password_length = random.randint(8, 11)
        return ''.join(random.choice(characters) for _ in range(password_length))