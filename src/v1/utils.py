import base64
from typing import Any
import aiohttp
from starlette import status
from starlette.responses import JSONResponse


async def download_and_convert_to_base64(image_url: str) -> str | None:
    """Download image from URL and convert to base64"""
    if not image_url:
        return None

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as response:
                if response.status == 200:
                    image_data = await response.read()
                    base64_image = base64.b64encode(image_data).decode('utf-8')
                    return f"data:image/jpeg;base64,{base64_image}"
                return None
    except Exception as e:
        print(f"Error downloading image: {str(e)}")
        return None

def create_response(
    status_code: int = status.HTTP_200_OK,
    detail: str = "Success",
    data: Any = None
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "status_code": status_code,
            "detail": detail,
            "data": data
        }
    )
