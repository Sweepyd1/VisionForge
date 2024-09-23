import aiofiles
from aiofiles import ospath as aiopath
from fastapi import Request
from fastapi import status
from fastapi.responses import FileResponse
from pydantic import BaseModel

from loader import db
from .errors import error_update_avatar
from .routers import protected, unprotected
from utils.other import is_base64_image


class ChangeAvatar(BaseModel):
    new_avatar: str


@protected.post("/get_my_account_info")
async def get_my_account_info(request: Request):
    user = (await db.get_user_by_username(request.state.user)).to_dict()
    del user["hashed_password"]
    del user["refresh_token"]
    return user


@protected.post("/change_my_avatar")
async def change_my_avatar(request: Request, avatar: ChangeAvatar):
    username = request.state.user
    image = is_base64_image(str(avatar.new_avatar))

    if image is not None:
        image: bytes
        filename: str = f"{username}.png"
        path: str = "General/avatars/users/" + filename

        async with aiofiles.open(path, "wb") as f:
            await f.write(image)

        return status.HTTP_200_OK

    return error_update_avatar


@unprotected.get("/users_avatars/")
@unprotected.get("/users_avatars/{username}")
async def users_avatars(request: Request, username: str = None):
    file_path: str = "General/avatars/default.png"

    if username is not None:
        new_path = "General/avatars/users/" + username
        if await aiopath.isfile(new_path) and await aiopath.exists(new_path):
            file_path = new_path

    return FileResponse(file_path, media_type="image/png")
