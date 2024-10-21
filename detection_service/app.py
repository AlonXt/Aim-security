from fastapi import FastAPI
from uvicorn import Config, Server

from detection_service.logs.logger import get_logger

logger = get_logger(__name__)


class App:
    def __init__(self, app: FastAPI, host: str, port: int, loop, router):
        self.app = app
        self.host = host
        self.port = port
        self.loop = loop
        self.router = router

    async def __uvicorn_server(self) -> None:
        logger.info("Starting the detection server")
        config_uvicorn = Config(app=self.app, host=self.host, port=self.port, loop=self.loop)
        await Server(config_uvicorn).serve()

    async def run(self) -> None:
        self.app.include_router(router=self.router.router)
        await self.__uvicorn_server()
