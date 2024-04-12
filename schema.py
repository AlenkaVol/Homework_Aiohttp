from abc import ABC
from typing import Optional

import pydantic


class AbstractUser(pydantic.BaseModel, ABC):
    name: str
    password: str

    @pydantic.field_validator("password")
    @classmethod
    def secure_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError(f"Minimal length of password is 8")
        return v


class CreateUser(AbstractUser):
    name: str
    password: str


class UpdateUser(AbstractUser):
    name: Optional[str] = None
    password: Optional[str] = None


class CreateAdvertisement(pydantic.BaseModel):
    title: str
    description: str
    owner: int


class UpdateAdvertisement(pydantic.BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    owner: Optional[int] = None
