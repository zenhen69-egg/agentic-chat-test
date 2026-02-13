import os
from agents import ModelSettings
from dotenv import load_dotenv

load_dotenv()

REQUIRED_FIELDS = ("full_name", "email", "bio")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
MODEL_SETTINGS = ModelSettings(temperature=0)
