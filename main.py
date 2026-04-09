import logging

import telebot
from db import Session, init_db
from functions import teach, get_reply, get_all_commands
import config


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(config.BOT_TOKEN, threaded=False)
init_db()
logger.info("Database initialized")


@bot.message_handler(commands=["start"])
def start_command(message):
    logger.info("Handling /start for chat_id=%s", message.chat.id)
    bot.reply_to(message, "Start successfully.")


@bot.message_handler(commands=["teach"])
def teach_command(message):
    logger.info("Handling /teach for chat_id=%s text=%r", message.chat.id, message.text)
    msg = message.text.split(" ")
    if len(msg) == 2:
        msg = msg[1].split(",")
        if len(msg) == 2:
            teach(message.chat.id, msg[0], msg[1])
            bot.reply_to(message, f"Done: {msg[0]} -> {msg[1]}")
        else:
            bot.reply_to(
                message, "Format is not correct, the format should be `keyword,reply`."
            )
    else:
        bot.reply_to(
            message, "No content, the format should be `/teach keyword,reply`."
        )


@bot.message_handler(commands=["listallcommands"])
def list_all_command(message):
    logger.info("Handling /listallcommands for chat_id=%s", message.chat.id)
    commands = get_all_commands()
    out = ""
    for command in commands:
        out += f"{command['keyword']} -> {command['reply']}\n"
    bot.send_message(message.chat.id, out)


@bot.message_handler(func=lambda msg: True)
def reply_messages_handler(message):
    logger.info(
        "Handling message for chat_id=%s text=%r", message.chat.id, message.text
    )
    reply = get_reply(message.text)
    if reply:
        bot.send_message(message.chat.id, reply)


if __name__ == "__main__":
    bot.remove_webhook()
    logger.info("Starting Telegram polling")
    try:
        bot.infinity_polling(skip_pending=True)
    except Exception:
        logger.exception("Polling stopped unexpectedly")
        raise
    finally:
        Session.remove()
        logger.info("Database sessions closed")
