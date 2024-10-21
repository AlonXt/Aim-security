from pydantic import BaseModel


class Settings(BaseModel):
    healthcare: bool
    finance: bool
    legal: bool
    hr: bool


class DetectionRequest(BaseModel):
    prompt: str
    settings: Settings
