import os
from pathlib import Path
from typing import Optional
from pydantic import BaseModel
from dotenv import load_dotenv

_ARTIFACTS_DIR = Path("artifacts")
(_ARTIFACTS_DIR / "logs").mkdir(parents=True, exist_ok=True)
(_ARTIFACTS_DIR / "screenshots").mkdir(parents=True, exist_ok=True)
(_ARTIFACTS_DIR / "videos").mkdir(parents=True, exist_ok=True)
(_ARTIFACTS_DIR / "junit").mkdir(parents=True, exist_ok=True)
(_ARTIFACTS_DIR / "allure").mkdir(parents=True, exist_ok=True)

# Load .env if present
load_dotenv(dotenv_path=Path(".env"), override=False)


class Selectors(BaseModel):
    # Mimir Chat selectors - hardcoded as they're specific to this chatbot implementation
    open_widget: str = "[data-testid='chatbot-icon']"
    input_area: str = "[data-testid=\"mimir-chat-input-field\"]"
    send_button: str = "[data-testid=\"mimir-chat-send-button\"]"
    messages_container: str = ".mimir-chat-container"
    message_row: str = ".mimir-chat-message"
    message_role_attr: str = "class"
    message_text: str = "p"


class Thresholds(BaseModel):
    # Default thresholds - individual tests override these as needed
    semantic_similarity_min: float = 0.75
    intent_confidence_min: float = 0.5


class OpenAIConfig(BaseModel):
    api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    chat_model: str = os.getenv("CHAT_MODEL", "gpt-4")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")


class Settings(BaseModel):
    base_url: str = os.getenv("BASE_URL", "https://sunrv-chatbot.dev02cms.milestoneinternet.info/?_enablechatbot=true")
    selectors: Selectors = Selectors()
    thresholds: Thresholds = Thresholds()
    openai: OpenAIConfig = OpenAIConfig()
    record_video: bool = os.getenv("RECORD_VIDEO", "true").lower() == "true"
    screenshot_on_failure: bool = os.getenv("SCREENSHOT_ON_FAILURE", "true").lower() == "true"


settings = Settings()




