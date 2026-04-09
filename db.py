from sqlalchemy import Integer, String, create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    scoped_session,
    sessionmaker,
)

import config


class Base(DeclarativeBase):
    pass


connect_args = (
    {"check_same_thread": False} if config.DATABASE_URI.startswith("sqlite") else {}
)
engine = create_engine(config.DATABASE_URI, connect_args=connect_args)
Session = scoped_session(sessionmaker(bind=engine))


class Pair(Base):
    __tablename__ = "pair"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    chat_id: Mapped[int] = mapped_column(Integer, nullable=False)
    keyword: Mapped[str] = mapped_column(String, nullable=False)
    reply: Mapped[str] = mapped_column(String, nullable=False)

    def __init__(self, chat_id, keyword, reply):
        self.chat_id = chat_id
        self.keyword = keyword
        self.reply = reply


def init_db():
    Base.metadata.create_all(engine)
