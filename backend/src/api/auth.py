from fastapi.responses import Response
from fastapi import HTTPException, Request
from email_validator import validate_email, EmailNotValidError

from loader import db, oauth2
from .routers import unprotected
from schemas.auth import Register, Login, UpdatedTokens
from .errors import username_exits_exc, login_data_exc, credentials_exc


@unprotected.post("/auth/register")
async def register(form: Register, response: Response):
	try:
		validated_email = validate_email(form.email)
		form.email = validated_email["email"]
	except EmailNotValidError:
		raise HTTPException(status_code=400, detail="Неверный email!")

	db_user = await db.get_user_by_username(username=form.username)

	if db_user:
		raise username_exits_exc

	await db.create_user(form.email, form.username, oauth2.get_password_hash(form.password), form.name)
	tokens: UpdatedTokens = await oauth2.update_access_and_refresh_tokens(form.username)
	response.set_cookie(key="access_token", value=tokens.access_token, httponly=True)
	response.set_cookie(key="refresh_token", value=tokens.refresh_token, httponly=True)
	response.status_code = 200
	return response


@unprotected.post("/auth/login")
async def login(form: Login, response: Response):
	user = await oauth2.validate_user(form.username, form.password)

	if not user:
		raise login_data_exc

	tokens = await oauth2.update_access_and_refresh_tokens(form.username)
	response.set_cookie(key="access_token", value=tokens.access_token, httponly=True)
	response.set_cookie(key="refresh_token", value=tokens.refresh_token, httponly=True)
	response.status_code = 200
	return response


@unprotected.post("/auth/is_authenticated")
async def is_authenticated(request: Request, response: Response):
	access_token = request.cookies.get('access_token', None)
	refresh_token = request.cookies.get('refresh_token', None)
	
	try:
		data = oauth2.check_auth_token(access_token)
		user = await db.get_user_by_username(data['username'])
		if user is not None:
			response.status_code = 200
			return response
	except Exception:
		data = oauth2.check_auth_token(refresh_token)
		user = await db.get_user_by_username(data['username'])
		if user is None or user["refresh_token"] != refresh_token:
			raise credentials_exc
		
		response.status_code = 200
		return response
	

@unprotected.post("/auth/logout")
async def logout(request: Request, response: Response):
	response.set_cookie(key="access_token", value="", httponly=True)
	response.set_cookie(key="refresh_token", value="", httponly=True)	
	response.status_code = 200
	return response
