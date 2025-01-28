import base64
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class AspNetSessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        # Generate ASP.NET style session ID
        session_id = f".AspNetCore.Session={base64.b64encode(uuid.uuid4().bytes).decode('utf-8')}"

        response = await call_next(request)

        # Add all typical ASP.NET Core headers
        response.headers["Server"] = "Microsoft-IIS/10.0"
        response.headers["X-Powered-By"] = "ASP.NET"
        response.headers["X-AspNet-Version"] = "8.0.21"
        response.headers["X-AspNetCore-Version"] = "8.0.21"
        response.headers["X-AspNetMvc-Version"] = "8.0"

        # Add typical ASP.NET Core Security Headers
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Add ASP.NET Core specific headers
        response.headers["Request-Context"] = f"appId=cid-v1:{uuid.uuid4()}"
        response.headers["Request-Id"] = f"|{uuid.uuid4().hex}.{uuid.uuid4().hex}"

        # Add  FAKE ASP.NET cookies
        response.set_cookie(
            ".AspNetCore.Session",
            session_id,
            max_age=3600,
            httponly=True,
            samesite="Lax"
        )

        # Add FAKE anti-forgery token cookie (common in ASP.NET)
        response.set_cookie(
            ".AspNetCore.Antiforgery",
            str(uuid.uuid4()),
            httponly=True,
            secure=True,
            samesite="Strict"
        )

        return response