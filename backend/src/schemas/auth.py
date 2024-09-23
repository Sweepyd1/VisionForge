from pydantic import BaseModel
from dataclasses import dataclass


class Register(BaseModel):
    email: str
    username: str
    password: str
    name: str


class Login(BaseModel):
    username: str
    password: str


class RefreshToken(BaseModel):
    refresh_token: str


@dataclass
class UpdatedTokens:
	access_token: str
	refresh_token: str
