# meow-bot
TG: @Meow_CatBot

made by @SiriusKoan https://github.com/SiriusKoan  
avatar by @kiri_487  

## setup
This project uses `uv` for environment and dependency management.

```bash
uv python install 3.12.11
uv sync
uv run python main.py
```

## docker
Run the bot with Docker Compose:

```bash
sudo docker compose up --build -d
```

Docker Compose loads variables from `.env`.

Required environment variables:

- `BOT_TOKEN`
- `GEMINI_API_KEY`

Optional environment variable:

- `DATABASE_URI` defaults to `sqlite:////app/data/data.db`
- `GEMINI_MODEL` defaults to `gemma-4-26b-a4b-it`
- `CHAT_HISTORY_MAX_LENGTH` defaults to `30`

## commands
`/teach`
Teach the bot with Keyword and bot_reply, like "Meow,meow0."  
`/weather`
Get Taipei weather.  
`/rm`
Remove specific reply.  
`/meow` or `/Meow`
Get a Pusheen sticker.  
`/capoo`
Get a Capoo sticker.  
`/cat`
get a cat photo.  
`/cancel`
Cancel current status.  

## features
Typing `\[msg]/`, the bot will reply the same message with bold font to you.  
  
Inline query can get random cat photo.
