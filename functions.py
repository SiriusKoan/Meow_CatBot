import sqlite3 as sql
import telebot
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
