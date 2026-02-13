import os
from agents import ModelSettings
from dotenv import load_dotenv

load_dotenv()

REQUIRED_FIELDS = ("sorter_id", "tag_serial_no")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
MODEL_SETTINGS = ModelSettings(temperature=0)
