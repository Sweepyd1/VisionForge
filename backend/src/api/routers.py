from typing import Callable
from fastapi.routing import APIRoute
from fastapi import APIRouter, Request, Response

from loader import oauth2, db
from .errors import credentials_exc
from schemas.auth import UpdatedTokens


class CustomAPIRoute(APIRoute):
	def get_route_handler(self) -> Callable:
		handler = super().get_route_handler()

		async def check_auth(request: Request) -> Response:
			access_token = request.cookies.get('access_token', None)
			refresh_token = request.cookies.get('refresh_token', None)

			if access_token and refresh_token:
				try:
					data = oauth2.check_auth_token(access_token)
					user = await db.get_user_by_username(data['username'])
					if user is not None:
						request.state.user = data['username']
						return await handler(request)
				except credentials_exc:
					data = oauth2.check_auth_token(refresh_token)
					user = await db.get_user_by_username(data['username'])
					if user is None or user["refresh_token"] != refresh_token:
						raise credentials_exc
					
					tokens: UpdatedTokens = await oauth2.update_access_and_refresh_tokens(data['username'])
					request.cookies["access_token"] = tokens.access_token
					request.cookies["refresh_token"] = tokens.refresh_token
					response = await handler(request)
					response.set_cookie(key="access_token", value=tokens.access_token)
					response.set_cookie(key="refresh_token", value=tokens.refresh_token)
					return response
			else:
				raise credentials_exc

		return check_auth


unprotected = APIRouter()
protected = APIRouter(prefix="/protected", route_class=CustomAPIRoute)
