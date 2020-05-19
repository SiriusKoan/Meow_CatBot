drop table if exists pair;
create table pair (
    id  INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id TEXT    NOT NULL,
    keyword TEXT    NOT NULL,
    reply   TEXT    NOT NULL
)

drop table if exists client;
create table client (
    id  INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id TEXT    NOT NULL,
    status  TEXT    NOT NULL
    -- status: none, teach, rm-select, rm-do, guess, guessing
)
