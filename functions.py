from db import db, Pair
import config

def teach(chat_id, keyword, reply):
    record = Pair(chat_id, keyword, reply)
    db.session.add(record)
    db.session.commit()

def get_reply(keyword):
    record = Pair.query.filter_by(keyword=keyword).first()
    if record:
        return record.reply
    else:
        return None

def get_all_commands():
    records = Pair.query.all()
    return [
        {
            "keyword": record.keyword,
            "reply": record.reply,
        }
        for record in records
    ]
