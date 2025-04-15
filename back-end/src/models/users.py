from enum import Enum
from typing import Optional
from pydantic import BaseModel, model_validator


class Role(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    GUEST = "GUEST"
    EMPLOYEE = "EMPLOYEE"

class SignIn(BaseModel):
    login: str
    password: str

class User(BaseModel):
    role: Role
    login: str
    name: str
    surname: str
    second_name: Optional[str] = None
    password: str
    email: Optional[str] = None
    contacts: Optional[str] = None
    # verified: bool = False

    @model_validator(mode="after")
    def validate(self):
        if (self.role == "GUEST" or self.role == "EMPLOYEE") and self.email is None:
            raise ValueError
        if (self.role == "GUEST" or self.role == "EMPLOYEE") and self.contacts is None:
            raise ValueError
        return self

class GetUserInfo(BaseModel):
    role: Role
    login: str
    name: str
    surname: str
    second_name: Optional[str] = None
    password: Optional[str] = None
    email: Optional[str] = None
    contacts: Optional[str] = None

class UserPatch(BaseModel):
    role: Optional[Role] = None
    login: Optional[str] = None
    name: Optional[str] = None
    surname: Optional[str] = None
    second_name: Optional[str] = None
    # password: Optional[str] = None
    email: Optional[str] = None
    contacts: Optional[str] = None