import json
import sqlite3
from datetime import datetime

from fastapi import APIRouter, Depends
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from detection_service import factory
from detection_service.logs.logger import get_logger
from detection_service.models.data_structures import DetectionRequest, Settings

logger = get_logger(__name__)


class DetectionRouter:
    def __init__(self, openai_client: OpenAI = Depends(factory.openai_client)):
        self.router = APIRouter()
        self.openai_client = openai_client
        self.add_routes()
        self.db_connection = self.__setup_database()

    def add_routes(self):
        @self.router.get("/")
        async def home():
            logger.info("Triggered home endpoint")
            return {"Data": "Hello, This is Alon's webapp built using FastAPI!"}

        @self.router.get("/logs")
        async def logs():
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT * FROM logs")
            logs = cursor.fetchall()
            return {"logs": logs}

        @self.router.post("/detect")
        async def detect(detection_request: DetectionRequest) -> dict:
            detected_topics = self.__detect_topics(detection_request.prompt, detection_request.settings)

            log_entry = {
                "time": datetime.utcnow().isoformat(),
                "detection_request": json.dumps(detection_request.dict()),
                "result": json.dumps(detected_topics)
            }
            self.__log_to_database(log_entry)

            return {"detected_topics": detected_topics}

    def __detect_topics(self, prompt: str, settings: Settings) -> dict:
        active_topics = self.__get_active_topics(settings)
        identify_topics_prompt = self.__create_identification_prompt(prompt, active_topics)
        response = self.__call_openai_api(identify_topics_prompt)
        detected_topics = self.__parse_openai_response(response, active_topics)
        return detected_topics

    def __get_active_topics(self, settings: Settings) -> list:
        return [
            topic for topic, is_active in [
                ("healthcare", settings.healthcare),
                ("finance", settings.finance),
                ("legal", settings.legal),
                ("hr", settings.hr)
            ] if is_active
        ]

    def __create_identification_prompt(self, prompt: str, active_topics: list) -> str:
        return f"""
        Please analyze the following prompt and determine if it relates to any of the following topics: {', '.join(active_topics)}.
        The prompt is: "{prompt}"
        Return a JSON object where each topic is a key lower cased and the value is true if the topic is present in the prompt, otherwise false.
        """

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def __call_openai_api(self, identify_topics_prompt: str) -> str:
        completion = self.openai_client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[{"role": "user", "content": identify_topics_prompt}]
        )
        return completion.choices[0].message.content

    def __parse_openai_response(self, response: str, active_topics: list) -> dict:
        try:
            detected_topics = json.loads(response)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON response from GPT: {response}")
            detected_topics = {topic: False for topic in active_topics}

        return detected_topics

    def __log_to_database(self, log_entry):
        cursor = self.db_connection.cursor()
        cursor.execute('''
            INSERT INTO logs (time, detection_request, result) VALUES (?, ?, ?)
        ''', (log_entry['time'], log_entry['detection_request'], log_entry['result']))
        self.db_connection.commit()

    def __setup_database(self):
        conn = sqlite3.connect('detection_logs.db')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                time TEXT,
                detection_request TEXT,
                result TEXT
            )
        ''')
        conn.commit()
        return conn
