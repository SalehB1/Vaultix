from contextlib import asynccontextmanager
from pathlib import Path
import redis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from configurations.cache import Cache
from configurations.middlewares import AspNetSessionMiddleware
from src.v1.views.login.email_auth import local_router as auth_email_router
from src.v1.views.login.phone_auth import local_router as auth_phone_router
from src.v1.views.login.MagicLink_auth import local_router as auth_magic_router
from src.v1.views.login.token_view import refresh_router
from src.v1.views.register.local_individual_register import router as reg_local_router
from src.v1.views.user.email_view import user_email_router
from src.v1.views.user.fogot_password_view import forgot_password_router
from src.v1.views.user.phone_view import user_phone_router
from src.v1.views.login.github_auth import github_router
from src.v1.views.login.google_auth import google_router

from starlette.types import ASGIApp
from configurations.environments import Values
import logging

from src.v1.views.user.profile_view import user_profile_router

BASE_DIR = str(Path(__file__).resolve().parent.parent)

logging.basicConfig(format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', filename=f'{BASE_DIR}/sys_log.log',
                    filemode='a')

# cache = Cache()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # await cache.initialize()
    yield
    # await cache.close()


app = FastAPI(root_path='/service', lifespan=lifespan,title='Authority Portal',version='1.2.0')
app.include_router(auth_email_router)
app.include_router(auth_phone_router)
app.include_router(auth_magic_router)
app.include_router(reg_local_router)
app.include_router(github_router)
app.include_router(google_router)
app.include_router(user_phone_router)
app.include_router(user_email_router)
app.include_router(user_profile_router)
app.include_router(forgot_password_router)
app.include_router(refresh_router)

origins = ['http://localhost:3000', 'http://localhost:8000', 'http://localhost:8080', 'http://localhost:8081',
           'http://localhost', 'http://127.0.0.1:8000', 'http://0.0.0.0:8000', 'frontend']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, security_headers: dict = None, blocked_headers: list = None) -> None:
        super().__init__(app)
        self.security_headers = security_headers or {}
        self.blocked_headers = blocked_headers or []

    async def dispatch(self, request, call_next):
        response = await call_next(request)
        for header_name, header_value in self.security_headers.items():
            response.headers[header_name] = header_value

        for header_name in self.blocked_headers:
            if header_name in response.headers:
                del response.headers[header_name]

        return response


security_headers = {
    "X-XSS-Protection": "1; mode=block",
    "X-Frame-Options": "DENY",
    # "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Cross-Origin-Embedder-Policy": "require-corp; report-to='default';",
    "Cross-Origin-Opener-Policy": "same-site; report-to='default';",
    "Cross-Origin-Resource-Policy": "same-site",
}

blocked_headers = [
    "Public-Key-Pins",
    "X-Powered-By",
    "X-AspNet-Version",
    "server",
    "X-AspNetMvc-Version",

]

app.add_middleware(SecurityHeadersMiddleware, security_headers=security_headers, blocked_headers=blocked_headers)
app.add_middleware(AspNetSessionMiddleware)


# Create admin

def get_redis_client():
    redis_con = redis.Redis.from_url(Values.REDIS_URL)
    return redis_con


@app.get("/")
async def root():
    return {"message": f"you are logged in"}
