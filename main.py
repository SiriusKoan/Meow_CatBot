import telebot
from flask import Flask, request
from functions import *
import config


bot = telebot.TeleBot(config.BOT_TOKEN)
server = Flask(__name__)

@server.route("/" + config.BOT_TOKEN, methods=["POST"])
def get_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return ""

@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=HEROKU_URL + BOT_TOKEN)
    return ""

@bot.message_handler(commands = ['start'])
def start_command(message):
    bot.reply_to(message, "Start successfully.")

@bot.message_handler(commands = ['teach'])
def teach_command(message):
    msg = message.text.split(",")
    if len(msg) == 2:
        teach(message.chat.id, msg[0], msg[1])
        bot.reply_to(message, f"Done: {msg[0]} -> {msg[1]}")
    else:
        bot.reply_to(message, "Format is not correct, the format should be `keyword,reply`")

@bot.message_handler(commands = ['listallcommands'])
def list_all_command(message):
    commands = get_all_commands()
    out = ""
    for command in commands:
        out += f"{command["keyword"]} -> {command["reply"]}\n"
    bot.send_message(message.chat.id, out)

@bot.message_handler(func = lambda msg: True)
def reply_messages_handler(message):
    reply = get_reply(message.text)
    if reply:
        bot.send_message(message.chat.id, reply)

bot.polling()
