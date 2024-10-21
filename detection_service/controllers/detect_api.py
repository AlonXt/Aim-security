import json
from datetime import datetime

from cachetools import TTLCache
from fastapi import APIRouter, Depends

from detection_service import factory
from detection_service.logs.logger import get_logger
from detection_service.models.data_structures import DetectionRequest, Settings
from openai import OpenAI

logger = get_logger(__name__)


class DetectionRouter:
    def __init__(self, openai_client: OpenAI = Depends(factory.openai_client)):
        self.router = APIRouter()
        self.openai_client = openai_client
        self.add_routes()
        self.logs_cache = TTLCache(maxsize=1000, ttl=600)

    def add_routes(self):
        @self.router.get("/")
        async def home():
            logger.info("triggered home endpoint")
            return {"Data": "Hello, This is Alon's webapp built using FastAPI!"}

        @self.router.get("/logs")
        async def logs():
            return {"logs": list(self.logs_cache.values())}

        @self.router.post("/detect")
        async def detect(detection_request: DetectionRequest) -> dict:
            detected_topics = await self.detect_topics(detection_request.prompt, detection_request.settings)

            log_entry = {
                "time": datetime.utcnow().isoformat(),
                "detection_request": detection_request,
                "result": detected_topics
            }
            self.logs_cache[datetime.utcnow().timestamp()] = log_entry

            return {"detected_topics": detected_topics}

    async def detect_topics(self, prompt: str, settings: Settings) -> dict:
        active_topics = [
            topic for topic, is_active in [
                ("Healthcare", settings.healthcare),
                ("Finance", settings.finance),
                ("Legal", settings.legal),
                ("HR", settings.hr)
            ] if is_active
        ]

        identify_topics_prompt = f"""
                Please analyze the following prompt and determine if it relates to any of the following topics: {', '.join(active_topics)}.
                The prompt is: "{prompt}"
                Return a JSON object where each topic is a key and the value is true if the topic is present in the prompt, otherwise false.
                """

        completion = self.openai_client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[{"role": "user", "content": identify_topics_prompt}]
        )

        response: str = completion.choices[0].message.content
        try:
            # RETRY MECHANISM
            detected_topics = json.loads(response)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON response from GPT: {response}")
            detected_topics = {topic: False for topic in active_topics}

        return detected_topics
