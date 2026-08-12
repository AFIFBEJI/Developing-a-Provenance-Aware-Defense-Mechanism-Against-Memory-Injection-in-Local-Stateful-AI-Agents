import os
from dotenv import load_dotenv

load_dotenv()

# Config du modèle local (agent attaqué)
LM_STUDIO_BASE_URL = "http://192.168.94.1:1234/v1"
LM_STUDIO_API_KEY = "not-needed"
MODEL_NAME = "qwen_qwen3-4b-instruct-2507"

# Config du juge externe (Gemini)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
JUDGE_MODEL_NAME = "gemini-3.1-flash-lite"