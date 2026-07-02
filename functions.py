import logging
import random
import re
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
        exact_records = session.query(Pair).filter_by(keyword=keyword).all()
        if exact_records:
            logger.info(
                "Matched exact keyword=%r with %s candidate replies",
                keyword,
                len(exact_records),
            )
            return random.choice(exact_records).reply

        regex_records = []
        for record in session.query(Pair).all():
            try:
                if re.fullmatch(record.keyword, keyword):
                    regex_records.append(record)
            except re.error:
                logger.warning("Skipped invalid regex keyword=%r", record.keyword)

        if regex_records:
            logger.info(
                "Matched regex keyword=%r with %s candidate replies",
                keyword,
                len(regex_records),
            )
            return random.choice(regex_records).reply

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
