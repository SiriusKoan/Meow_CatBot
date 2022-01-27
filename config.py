from os import getenv, urandom

BOT_TOKEN = getenv("BOT_TOKEN")
HEROKU_URL = getenv("HEROKU_URL")

class Config:
    SECRET = urandom(32)
    SQLALCHEMY_DATABASE_URI = getenv("DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False