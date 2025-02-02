import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = str(Path(__file__).resolve().parent.parent)
load_dotenv(os.path.join(BASE_DIR, '.env'))


class Values:


    @staticmethod
    def get_boolean_env_var(var_name, default_value):
        value = os.getenv(var_name, default_value)
        return value.lower() in ['true', '1', 't', 'y', 'yes']

    EMAIL_API_URL = os.getenv('EMAIL_API_URL', None)
    EMAIL_API_KEY = os.getenv('EMAIL_API_KEY', None)
    REDIS_SOCKET_CONNECT_TIMEOUT = int(os.getenv('REDIS_SOCKET_CONNECT_TIMEOUT'))
    REDIS_SOCKET_TIMEOUT = int(os.getenv('REDIS_SOCKET_TIMEOUT'))
    FORGET_PASSWORD_CODE_EXPIRE_TIME_MINUTES = os.getenv('FORGET_PASSWORD_CODE_EXPIRE_TIME_MINUTES')
    FORGET_PASSWORD_TEMPLATE_ID = os.getenv('FORGET_PASSWORD_TEMPLATE_ID')
    EMAIL_CHANGE_OTP_EXPIRE_TIME_MINUTES = (os.getenv('EMAIL_CHANGE_OTP_EXPIRE_TIME_MINUTES', None))
    COMPANY_NAME = os.getenv('COMPANY_NAME', '')
    PHONE_OTP_EXPIRE_TIME_MINUTES = os.getenv('PHONE_OTP_EXPIRE_TIME_MINUTES', None)
    CHANGE_PHONE_TEMPLATE_ID = os.getenv('CHANGE_PHONE_TEMPLATE_ID', None)
    NEW_PHONE_TEMPLATE_ID = os.getenv('NEW_PHONE_TEMPLATE_ID', None)
    VERIFY_EMAIL_PATH = os.getenv('VERIFY_EMAIL_PATH')
    REDIS_URL = os.getenv("CACHE_URL", "redis://localhost")
    JWT_EMAIL_SECRET_KEY = os.getenv('JWT_EMAIL_SECRET_KEY', None)
    OTP_EXPIRE_TIME_MINUTES = os.getenv('OTP_EXPIRE_TIME_MINUTES', 5)
    LOGIN_OTP_TEMPLATE_ID = int(os.getenv('LOGIN_OTP_TEMPLATE_ID', None))
    MSGWAY_API_KEY = os.getenv('MSGWAY_API_KEY', '123456789')
    MSGWAY_API_URL = os.getenv('MSGWAY_API_URL', 'none')
    MSGWAY_PROVIDER = int(os.getenv('MSGWAY_PROVIDER', 1))
    EMAIL_TOKEN_EXPIRE_MINUTES = os.getenv('EMAIL_TOKEN_EXPIRE_MINUTES')
    RUN_MODE = os.getenv('RUN_MODE', 'dev')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET', None)
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', None)
    GITHUB_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET', None)
    GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID', None)
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_FROM = os.getenv("MAIL_FROM")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "Your App Name")
    MAIL_STARTTLS = os.getenv('MAIL_STARTTLS', None)
    MAIL_SSL_TLS = os.getenv('MAIL_SSL_TLS', None)
    USE_CREDENTIALS = os.getenv('USE_CREDENTIALS', True)
    TEMPLATE_FOLDER = os.path.join(BASE_DIR, 'email_templates')
    JWT_REFRESH_SECRET_KEY = os.getenv('JWT_REFRESH_SECRET_KEY', None)
    SENTRY = None
    MEDIA_FOLDER_PATH = os.getenv('MEDIA_FOLDER_PATH', 'media')
    E_H_TOKEN = os.getenv('E_H_TOKEN')
    PASSWORD_TOKEN_EXPIRE_MINUTES = os.getenv('PASSWORD_TOKEN_EXPIRE_MINUTES', 20)
    MAIL_GATEWAY = os.getenv('MAIL_GATEWAY', 'smtp.gmail.com')
    LOCAL_HOST_EMAIL = os.getenv('LOCAL_HOST_EMAIL', 'localhost')
    EMAIL_PORT = os.getenv('EMAIL_PORT', 587)
    EMAIL_SENDER = os.getenv('EMAIL_SENDER', 'icsportal@um.ir')
    Workers = int(os.getenv('WORKERS', 10))
    FORWARDED_ALLOW_IPS = os.getenv('FORWARDED_ALLOW_IPS', '*')
    BASE_URL = os.getenv('BASE_URL', 'http://localhost:8002')
    EMAIL_FROM = os.getenv('EMAIL_FROM', 'info@example.com')
    TimeWindow = os.getenv("TimeWindow", 10)
    RateLimit = os.getenv("RateLimit", 15)
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
    DB_NAME = os.getenv("DB_NAME", "postgres")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_CONFIG = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = os.getenv("REDIS_PORT", "61709")
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
    REDIS_DB = os.getenv("REDIS_DB", "0")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_TIME', 120))
    REFRESH_TOKEN_EXPIRE_MINUTES = int(os.getenv('REFRESH_TOKEN_TIME', 14400))
    ALGORITHM = os.getenv('ALGORITHM', 'HS512')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', '')
    SMS_API_KEY = os.getenv('SMS_API_KEY', '')
    COOKIE_URL = os.getenv('COOKIE_URL', 'http://localhost:8002')
    COOKIE_NAME = os.getenv('COOKIE_NAME', None)
    GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', None)
    GITHUB_REDIRECT_URI = os.getenv('GITHUB_REDIRECT_URI', None)
    VERIFY_EMAIL_CALLBACK = os.getenv('VERIFY_EMAIL_CALLBACK', None)
    MAGIC_LINK_CALLBACK = os.getenv('MAGIC_LINK_CALLBACK', None)
