from pydantic import BaseModel


class AuthURLResponse(BaseModel):
    url: str

class GoogleUserResponse(BaseModel):
    email: str
    google_id: str
    access_token: str
    name: str | None
    profile_image: str | None
