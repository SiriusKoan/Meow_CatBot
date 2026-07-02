def parse_teach_command_text(text):
    parts = text.split(maxsplit=1)
    if len(parts) != 2 or not parts[1].strip():
        return None, None

    payload = parts[1].strip()
    if "," not in payload:
        raise ValueError("Teach command payload must contain a comma")

    keyword, reply = payload.split(",", 1)
    keyword = keyword.strip()
    reply = reply.strip()
    if not keyword or not reply:
        raise ValueError("Teach command keyword and reply must not be empty")

    return keyword, reply
