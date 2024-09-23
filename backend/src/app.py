import uvloop
import uvicorn
import asyncio
from loguru import logger
from fastapi import FastAPI

from loader import app
from data import config as cfg
from api.routers import unprotected, protected
from api import auth
from api import account


def setup_app(application: FastAPI) -> None:
	application.include_router(unprotected, prefix="/api")
	application.include_router(protected, prefix="/api")


if __name__ == "__main__":
	setup_app(app)
	
	try:
		asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
		logger.info("uvloop installed")
	except Exception:
		logger.warning("uvloop not installed")
		
	uvicorn.run(app, host=cfg.API_HOST, port=cfg.API_PORT)
