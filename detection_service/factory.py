import os
from functools import lru_cache

from fastapi import FastAPI
from openai import OpenAI


def main_app() -> FastAPI:
    return FastAPI()


@lru_cache()
def openai_client() -> OpenAI:
    return OpenAI(
        api_key=os.getenv('OPENAI_API_KEY'),
        base_url=os.getenv('OPENAI_URL'),
    )
