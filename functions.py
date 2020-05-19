import sqlite3 as sql
import telebot
import requests
import json
import urllib.parse
from random import shuffle, randint
import time
import datetime
import config

def start(chat_id):
    con = sql.connect("data.db")
    cur = con.cursor()
    cur.execute('SELECT * FROM client WHERE chat_id = ?', (chat_id,))

    if_exist = cur.fetchall()
    if if_exist == []:
        cur.execute('INSERT INTO client (chat_id, status) VALUES (?, ?)', (chat_id, "none"))
    else:
        cur.execute('UPDATE client SET status = "none" WHERE chat_id = ?', (chat_id,))

    con.commit()
    con.close()  

def set_status(new_status, chat_id):
    con = sql.connect("data.db")
    cur = con.cursor()
    cur.execute('UPDATE client SET status = ? WHERE chat_id = ?', (new_status, str(chat_id)))
    con.commit()
    con.close()

def teach(msg, chat_id):
    msg = msg.split(",")
    con = sql.connect("data.db")
    cur = con.cursor()
    cur.execute('INSERT INTO pair (chat_id, keyword, reply) VALUES (?, ?, ?)', (str(chat_id), msg[0], msg[1]))
    con.commit()
    con.close()

    set_status("none", chat_id)
    
def rm_select(msg, chat_id):
    con = sql.connect('data.db')
    cur = con.cursor()
    cur.execute('SELECT reply FROM pair WHERE chat_id = ? AND keyword = ?', (chat_id, msg))
    reply = cur.fetchall()
    con.close()

    markup = telebot.types.ReplyKeyboardMarkup(row_width = 2)
    options = []
    for option in reply:
        options.append(option[0])
    markup.add(*options)
    set_status("rm-do", chat_id)
    return markup

def rm_do(msg, chat_id):
    con = sql.connect("data.db")
    cur = con.cursor()
    cur.execute("DELETE FROM pair WHERE reply = ? AND chat_id = ?", (msg, chat_id))
    con.commit()
    con.close()
    set_status("none", chat_id)

def get_weather(msg, chat_id):
    import pyowm
    key = pyowm.OWM(config.OWM_TOKEN)
    location = key.weather_at_place("Taipei")
    result = location.get_weather()

    humidity = str(result.get_humidity()) + "%"
    temperature = str(round(result.get_temperature('celsius')['temp'], 1)) + "°C"
    temperature_range = str(result.get_temperature('celsius')['temp_min']) + "°C" + "~" + str(result.get_temperature('celsius')['temp_max']) + "°C"

    set_status("none", chat_id)

    return (humidity, temperature, temperature_range)

# get air condition (AQI)
def get_AQI(msg, chat_id):
    data_link = "http://opendata.epa.gov.tw/webapi/Data/REWIQA/?$select=SiteName,County,AQI,Status&$orderby=SiteName&$skip=0&$top=1000&format=json"
    con = requests.get(data_link)
    if con.ok:
        data = con.text
        json_data = json.loads(data)
        for site_data in json_data:
            if site_data['SiteName'] == msg:
                set_status("none", chat_id)
                return site_data
    else:
        return "Something went wrong...\nPlease wait."
