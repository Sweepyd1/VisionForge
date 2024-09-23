from loguru import logger
from fastapi import FastAPI
from contextlib import asynccontextmanager
from starlette.middleware.cors import CORSMiddleware

from data.database import DB
from data import config as cfg
from utils.oauth2_utils import OAuth2Utils


@asynccontextmanager
async def lifespan(_):
    await db.init_database()
    yield
    logger.info("Завершение работы сервера!")
    await db.close()


db: DB = DB()
app: FastAPI = FastAPI(lifespan=lifespan, debug=True)

oauth2: OAuth2Utils = OAuth2Utils(
    db=db,
    jwt_token_secret=cfg.JWT_TOKEN_SECRET,
    access_token_exp=cfg.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    refresh_token_exp=cfg.JWT_REFRESH_TOKEN_EXPIRE_MINUTES,
    jwt_algorithm=cfg.JWT_ALGORITHM,
    token_url="/api/auth/login"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
