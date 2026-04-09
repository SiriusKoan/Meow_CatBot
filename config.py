from os import getenv

BOT_TOKEN = getenv("BOT_TOKEN")
DATABASE_URI = getenv("DATABASE_URI", "sqlite:////app/data/data.db")
