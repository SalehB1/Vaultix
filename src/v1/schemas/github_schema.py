from pydantic import BaseModel


class AuthURLResponse(BaseModel):
    url: str

class GitHubUserResponse(BaseModel):
    email: str
    github_id: str
    access_token: str
    name: str | None
    profile_image: str | None  # Changed from avatar_url to profile_image
