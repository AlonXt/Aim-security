import asyncio
import os


from detection_service import factory
from detection_service.app import App
from detection_service.controllers.detect_api import DetectionRouter


def run_server():
    loop = asyncio.get_event_loop()
    detection_router = DetectionRouter(factory.openai_client())
    app = App(
        app=factory.main_app(),
        router=detection_router,
        loop=loop,
        host=os.getenv("UVICORN_IP"),
        port=int(os.getenv("UVICORN_PORT"))
    )
    loop.run_until_complete(app.run())


if __name__ == '__main__':
    run_server()
