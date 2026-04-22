import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL")
MODEL = os.getenv("MODEL")

CLICKUP_API_KEY = os.getenv("CLICKUP_API_KEY")
CLICKUP_TASK_ID = os.getenv("CLICKUP_TASK_ID")