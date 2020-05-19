import telebot
from telebot import types
import sqlite3 as sql
import logging
import random
import datetime
from functions import *
from os import system
import config

                                            
bot = telebot.TeleBot(config.BOT_TOKEN)


# log
logger = telebot.logger

system("mkdir log")

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_filename = datetime.datetime.now().strftime("log/%Y-%m-%d.log")

file_handler = logging.FileHandler(log_filename)
logger.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


@bot.message_handler(commands = ['start'])
def start_main(message):
    bot.reply_to(message, "Start successfully.")
    bot.send_message(message.chat.id, "This bot is used for echoing 'meow'\nTyping /meow for meow ><")
    start(message.chat.id)                    
                                                                
@bot.message_handler(commands = ['meow', 'Meow'])
def send_meow(message):
    sti = open("../stickers/Pusheen/Pusheen%s.webp"%str(random.randint(1, 30)), "rb")
    bot.send_sticker(message.chat.id, sti)

@bot.message_handler(commands = ['capoo'])
def capoo_tgs(message):
    sti = open("../stickers/capoo_tgs/tgs%s.tgs"%str(random.randint(1, 50)), "rb")
    bot.send_sticker(message.chat.id, sti)

@bot.message_handler(commands = ['cat'])
def cat_photo(message):
    r = requests.get("https://source.unsplash.com/random?cat")
    bot.send_photo(message.chat.id, r.content)

@bot.message_handler(commands = ['teach'])
def teach_tip(message):
    bot.reply_to(message, "Teach this bot to talk!\nFormat: keyword,bot's reply")
    set_status("teach", message.chat.id)

@bot.message_handler(commands = ['rm'])
def rm_tip(message):
    bot.reply_to(message, "Enter the keyword you want to remove.")
    set_status("rm-select", message.chat.id)

@bot.message_handler(commands = ['weather'])
def weather(message):
    humidity, temperature, temperature_range = get_weather(message.text, message.chat.id)
    bot.send_message(message.chat.id, "*Taipei Weather*: \nHumidity: %s\nTemperature: %s\nTemperature range: %s"%(humidity, temperature, temperature_range), parse_mode="Markdown")

@bot.message_handler(commands = ['guess'])
def enter_guess_number(message):
    bot.send_message(message.chat.id, "Enter two numbers and split them with a space:")
    set_status("guess", message.chat.id)

@bot.message_handler(commands = ['cancel'])
def cancel(message):
    set_status("none", message.chat.id)
    bot.send_message(message.chat.id, "Cancel.")

@bot.message_handler(commands = ['listallcommands'])
def list_all(message):
    con = sql.connect('data.db')
    cur = con.cursor()
    cur.execute('SELECT keyword, reply FROM pair')
    commands = cur.fetchall()
    con.close()

    out = ""
    for command in commands:
        out = out + str(command) + '\n'
    bot.send_message(message.chat.id, out)

# get air condition
@bot.message_handler(commands = ['air'])
def ait_condition(message):
	set_status("air", message.chat.id)
	bot.send_message(message.chat.id, "Enter the site name to get the AQI.\n", parse_mode="Markdown")

@bot.inline_handler(lambda query: True)
def cat_photo_inline(query):
    r = requests.get('https://source.unsplash.com/random?cat')
    response = [(types.InlineQueryResultPhoto(0, photo_url = r.url, thumb_url = r.url))]
    bot.answer_inline_query(query.id, response, cache_time = 30)

@bot.message_handler(func = lambda msg: True)
def handle_normal_msg(message):
    msg = message.text
    chat_id = message.chat.id

    con = sql.connect('data.db')
    cur = con.cursor()
    cur.execute('SELECT status FROM client WHERE chat_id = ?', (chat_id,))
    status = cur.fetchall()
    if status == []:
        bot.send_message(chat_id, "You have to /start first.")
    else:
        status = status[0][0]
    con.close()

    if status == "teach":
        if "," in msg:
            teach(msg, chat_id)
            bot.send_message(message.chat.id, "Success!")
        else:
            bot.reply_to(message, "The format is not correct...\nFormat: keyword,bot's reply")
    elif status == "rm-select":
        bot.send_message(chat_id, "Choose one reply you want to delete:", reply_markup = rm_select(msg, chat_id))
    elif status == "rm-do":
        rm_do(msg, chat_id)
        # remove markup
        bot.send_message(message.chat.id, "Success!", reply_markup = telebot.types.ReplyKeyboardRemove(selective=False))
    elif status == "air":
        reply = get_AQI(msg, chat_id)
        if reply == None:
            county = reply['County']
            sitename = reply['SiteName']
            AQI = reply['AQI']
            status = reply['Status']
            bot.send_message(chat_id, "*County:* %s\n*Site Name:* %s\n*AQI:* %s\n*Status:* %s"%(county, sitename, AQI, status), parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, "There is not this site...")
    elif message.text.count("\\") == 1 and message.text.count("/") == 1 and message.text.index("\\") == 0 and message.text.index("/") == len(message.text) - 1:
       bot.reply_to(message, "*%s*"%message.text, parse_mode = "Markdown")
    else:
        con = sql.connect("data.db")
        cur = con.cursor()
        cur.execute('SELECT reply FROM pair WHERE keyword = ?', (msg,))
        out = cur.fetchall()
        con.close()
        if out != []:
            bot.send_message(message.chat.id, out[random.randint(0, len(out)-1)])


bot.polling()
