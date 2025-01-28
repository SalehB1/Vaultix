from typing import Optional, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar('T')


class APIResponse(BaseModel, Generic[T]):
    status_code: int
    detail: str
    data: Optional[T] = None

    class Config:
        json_schema_extra = {
            "example": {
                "status_code": 200,
                "detail": "Operation completed successfully",
                "data": None
            }
        }
