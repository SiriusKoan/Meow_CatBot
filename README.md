# meow-bot
TG: @Meow_CatBot

made by @SiriusKoan https://github.com/SiriusKoan  
avatar by @kiri_487  

## setup
This project uses `uv` for environment and dependency management.

```bash
uv python install 3.12.11
uv sync
uv run gunicorn main:server
```

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
