import logging
import random
from db import Pair, Session

logger = logging.getLogger(__name__)


def teach(chat_id, keyword, reply):
    session = Session()
    try:
        record = Pair(chat_id, keyword, reply)
        session.add(record)
        session.commit()
        logger.info("Stored reply mapping for chat_id=%s keyword=%r", chat_id, keyword)
    finally:
        Session.remove()


def get_reply(keyword):
    session = Session()
    try:
        records = session.query(Pair).filter_by(keyword=keyword).all()
        if records:
            logger.info(
                "Matched keyword=%r with %s candidate replies", keyword, len(records)
            )
            return random.choice(records).reply
        else:
            logger.info("No reply configured for keyword=%r", keyword)
            return None
    finally:
        Session.remove()


def get_all_commands():
    session = Session()
    try:
        records = session.query(Pair).all()
        logger.info("Loaded %s stored command mappings", len(records))
        return [
            {
                "keyword": record.keyword,
                "reply": record.reply,
            }
            for record in records
        ]
    finally:
        Session.remove()
