from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Pair(db.Model):
    __tablename__ = "pair"
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, nullable=False)
    keyword = db.Column(db.String, nullable=False)
    reply = db.Column(db.String, nullable=False)

    def __init__(self, chat_id, keyword, reply):
        self.chat_id = chat_id
        self.keyword = keyword
        self.reply = reply
