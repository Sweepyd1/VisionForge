from jose import jwt
from typing import Optional
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer

from data.database import DB
from api.errors import credentials_exc
from schemas.auth import UpdatedTokens


class OAuth2Utils:
	def __init__(
			self, db: DB, jwt_token_secret: str,
			access_token_exp: int, refresh_token_exp: int,
			jwt_algorithm: str = "HS256", token_url="/api/auth/login") -> None:
		self.db: DB = db
		self.jwt_token_secret = jwt_token_secret
		self.access_token_exp = access_token_exp
		self.refresh_token_exp = refresh_token_exp
		self.jwt_algorithm = jwt_algorithm
		self.token_url = token_url

	@property
	def oauth2_scheme(self) -> OAuth2PasswordBearer:
		return OAuth2PasswordBearer(tokenUrl=self.token_url)

	@property
	def pwd_context(self) -> CryptContext:
		return CryptContext(schemes=["bcrypt"], deprecated="auto")

	def verify_password(self, plain_password, hashed_password) -> bool:
		return self.pwd_context.verify(plain_password, hashed_password)

	def get_password_hash(self, password) -> str:
		return self.pwd_context.hash(password)

	def check_auth_token(self, token: str) -> dict:
		decoded = self.decode_token(token)
		try:
			if decoded is not None and "exp" in decoded and "username" in decoded:
				if datetime.utcnow() < datetime.fromtimestamp(decoded["exp"]):
					return decoded
		except Exception: ...

		raise credentials_exc

	def decode_token(self, token: str) -> Optional[dict]:
		try:
			return jwt.decode(
				token,
				self.jwt_token_secret,
				algorithms=self.jwt_algorithm
			)
		except:
			return None

	async def create_access_token(self, data: dict):
		to_encode = data.copy()
		to_encode.update({"exp": datetime.utcnow() + timedelta(minutes=self.access_token_exp)})
		encoded_jwt = jwt.encode(to_encode, self.jwt_token_secret, algorithm=self.jwt_algorithm)
		return encoded_jwt

	async def create_refresh_token(self, data: dict):
		to_encode = data.copy()
		to_encode.update({"exp": datetime.utcnow() + timedelta(minutes=self.refresh_token_exp)})
		encoded_jwt = jwt.encode(to_encode, self.jwt_token_secret, algorithm=self.jwt_algorithm)
		return encoded_jwt

	async def validate_user(self, username: str, password: str):
		user = await self.db.get_user_by_username(username=username)

		if not user or not self.verify_password(password, user["hashed_password"]):
			return False

		return user.to_dict()
	
	async def update_access_and_refresh_tokens(self, username: str) -> UpdatedTokens:
		access_token = await self.create_access_token(data={"username": username})
		refresh_token = await self.create_refresh_token(data={"username": username})
		await self.db.update_refresh_token_by_username(username, refresh_token)
		return UpdatedTokens(access_token, refresh_token)
