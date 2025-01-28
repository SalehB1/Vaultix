from pydantic import BaseModel
from typing import Optional, TypeVar, Generic

T = TypeVar('T')


class ResponseSchema(BaseModel, Generic[T]):
    status_code: int
    detail: str
    result: Optional[T] = None
