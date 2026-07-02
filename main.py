from collections import defaultdict, deque
import html
import logging

import telebot
from google import genai
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

chat_histories = defaultdict(lambda: deque(maxlen=config.CHAT_HISTORY_MAX_LENGTH))
gemini_client = genai.Client(api_key=config.GEMINI_API_KEY) if config.GEMINI_API_KEY else None
bot_identity = {"id": None, "username": None}


def extract_bold_echo(text):
    if not text or len(text) < 3:
        return None
    if text.startswith("\\") and text.endswith("/"):
        content = text[1:-1]
        if content:
            return content
    return None


def get_sender_name(message):
    if not message.from_user:
        return "unknown"
    if message.from_user.username:
        return f"@{message.from_user.username}"
    if message.from_user.first_name:
        return message.from_user.first_name
    return str(message.from_user.id)


def add_history(chat_id, role, text, sender, message_id=None, reply_to=None):
    if not text:
        return
    entry = {"role": role, "sender": sender, "text": text, "reactions": {}}
    if message_id is not None:
        entry["message_id"] = message_id
    if reply_to:
        entry["reply_to"] = reply_to
    chat_histories[chat_id].append(entry)


def find_history_entry(chat_id, message_id):
    for entry in chat_histories[chat_id]:
        if entry.get("message_id") == message_id:
            return entry
    return None


def get_reply_to(message):
    replied = message.reply_to_message
    if not replied:
        return None
    sender = get_sender_name(replied) if replied.from_user else "unknown"
    text = replied.text or replied.caption or "(media)"
    return {"sender": sender, "text": text}


def send_and_record(chat_id, text, parse_mode=None):
    sent = bot.send_message(chat_id, text, parse_mode=parse_mode)
    add_history(chat_id, "assistant", text, "Meow_CatBot", message_id=sent.message_id)


def get_bot_identity():
    if bot_identity["id"] is None or bot_identity["username"] is None:
        me = bot.get_me()
        bot_identity["id"] = me.id
        bot_identity["username"] = me.username
    return bot_identity


def is_group_mention(message):
    if message.chat.type not in ("group", "supergroup"):
        return False
    try:
        identity = get_bot_identity()
    except Exception:
        logger.exception("Failed to fetch bot identity for mention detection")
        return False

    if (
        message.reply_to_message
        and message.reply_to_message.from_user
        and message.reply_to_message.from_user.id == identity["id"]
    ):
        return True

    text = message.text or ""
    entities = message.entities or []
    expected_mention = f"@{identity['username']}".lower()
    for entity in entities:
        if entity.type == "mention":
            mention = text[entity.offset : entity.offset + entity.length].lower()
            if mention == expected_mention:
                return True
    return expected_mention in text.lower()


def build_gemini_prompt(chat_id):
    history_lines = []
    for item in chat_histories[chat_id]:
        meta = []
        if item.get("reply_to"):
            rt = item["reply_to"]
            meta.append(f"replying to {rt['sender']}: \"{rt['text']}\"")
        reactions = {e: c for e, c in item.get("reactions", {}).items() if c > 0}
        if reactions:
            reaction_str = ", ".join(f"{emoji}×{count}" for emoji, count in reactions.items())
            meta.append(f"reactions: {reaction_str}")
        prefix = f"{item['role']} ({item['sender']})"
        if meta:
            prefix += f" [{'; '.join(meta)}]"
        history_lines.append(f"{prefix}: {item['text']}")
    return (
        "You are Meow_CatBot in a Telegram group chat. "
        "Reply warm, naturally and concisely to the messages when the bot is mentioned. And do whatever the group members ask you to do. "
        "Use the recent chat history below as context.\n\n"
        "Recent chat history:\n"
        f"{chr(10).join(history_lines)}"
    )


def generate_gemini_reply(chat_id):
    if not gemini_client:
        logger.warning("Gemini API key is not configured; skipping AI reply")
        return None
    response = gemini_client.models.generate_content(
        model=config.GEMINI_MODEL,
        contents=build_gemini_prompt(chat_id),
    )
    if response.text:
        return response.text.strip()
    return None


@bot.message_handler(commands=["start"])
def start_command(message):
    logger.info("Handling /start for chat_id=%s", message.chat.id)
    add_history(message.chat.id, "user", message.text, get_sender_name(message),
                message_id=message.message_id, reply_to=get_reply_to(message))
    send_and_record(message.chat.id, "Start successfully.")


@bot.message_handler(commands=["teach"])
def teach_command(message):
    logger.info("Handling /teach for chat_id=%s text=%r", message.chat.id, message.text)
    add_history(message.chat.id, "user", message.text, get_sender_name(message),
                message_id=message.message_id, reply_to=get_reply_to(message))
    msg = message.text.split(" ")
    if len(msg) == 2:
        msg = msg[1].split(",")
        if len(msg) == 2:
            teach(message.chat.id, msg[0], msg[1])
            send_and_record(message.chat.id, f"Done: {msg[0]} -> {msg[1]}")
        else:
            send_and_record(
                message.chat.id, "Format is not correct, the format should be `keyword,reply`."
            )
    else:
        send_and_record(
            message.chat.id, "No content, the format should be `/teach keyword,reply`."
        )


@bot.message_handler(commands=["listallcommands"])
def list_all_command(message):
    logger.info("Handling /listallcommands for chat_id=%s", message.chat.id)
    add_history(message.chat.id, "user", message.text, get_sender_name(message),
                message_id=message.message_id, reply_to=get_reply_to(message))
    commands = get_all_commands()
    out = ""
    for command in commands:
        out += f"{command['keyword']} -> {command['reply']}\n"
    send_and_record(message.chat.id, out)


@bot.message_handler(func=lambda msg: True)
def reply_messages_handler(message):
    logger.info(
        "Handling message for chat_id=%s text=%r", message.chat.id, message.text
    )
    add_history(message.chat.id, "user", message.text, get_sender_name(message),
                message_id=message.message_id, reply_to=get_reply_to(message))

    bold_echo = extract_bold_echo(message.text)
    if bold_echo:
        logger.info("Matched bold echo pattern for chat_id=%s", message.chat.id)
        send_and_record(
            message.chat.id,
            f"<b>{html.escape(bold_echo)}</b>",
            parse_mode="HTML",
        )
        return

    if is_group_mention(message):
        logger.info("Matched bot mention for chat_id=%s", message.chat.id)
        try:
            reply = generate_gemini_reply(message.chat.id)
        except Exception:
            logger.exception("Gemini reply generation failed for chat_id=%s", message.chat.id)
            reply = None
        if reply:
            send_and_record(message.chat.id, reply)
            return

    reply = get_reply(message.text)
    if reply:
        send_and_record(message.chat.id, reply)


@bot.message_reaction_handler(func=lambda reaction: True)
def reaction_handler(reaction):
    chat_id = reaction.chat.id
    message_id = reaction.message_id
    entry = find_history_entry(chat_id, message_id)
    if entry is None:
        return
    reactions = entry["reactions"]
    old_emojis = {r.emoji for r in reaction.old_reaction if r.type == "emoji"}
    new_emojis = {r.emoji for r in reaction.new_reaction if r.type == "emoji"}
    for emoji in old_emojis - new_emojis:
        if reactions.get(emoji, 0) > 0:
            reactions[emoji] -= 1
    for emoji in new_emojis - old_emojis:
        reactions[emoji] = reactions.get(emoji, 0) + 1


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
