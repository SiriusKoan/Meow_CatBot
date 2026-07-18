from os import getenv

BOT_TOKEN = getenv("BOT_TOKEN")
DATABASE_URI = getenv("DATABASE_URI", "sqlite:////app/data/data.db")
GEMINI_API_KEY = getenv("GEMINI_API_KEY")
GEMINI_MODEL = getenv("GEMINI_MODEL", "gemma-4-26b-a4b-it")
CHAT_HISTORY_MAX_LENGTH = int(getenv("CHAT_HISTORY_MAX_LENGTH", "30"))
SKILLS_DIR = getenv("SKILLS_DIR", "skills")
