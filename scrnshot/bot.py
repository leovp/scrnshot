import asyncio
import os
import textwrap
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from functools import partial

import aiotg
import validators

from .screenshot import do_screenshot

bot = aiotg.Bot(api_token=os.getenv('TG_BOT_TOKEN'))
queue = defaultdict(partial(deque, maxlen=10))
pool = ThreadPoolExecutor(max_workers=2)


@bot.command('^/(start|help)$')
async def echo(chat: aiotg.Chat, match):
    await chat.send_text(textwrap.dedent("""
        bleep bloop I'm a bot 🤖
        Throw me an URL and I'll screenshot it for you.
    """))


@bot.command('(.+)')
async def screenshot(chat: aiotg.Chat, match):
    loop = asyncio.get_event_loop()

    url, = match.groups()

    if not url.startswith(('http://', 'https://')):
        # HTTP to HTTPS redirects are a thing, so it's a safer bet.
        url = 'http://' + url

    # Disallow `localhost`, `192.168.1.1` and so on.
    if not validators.url(url, public=True):
        await chat.send_text('Wrong URL 😳')
        return

    if len(queue[chat.id]) == 10:
        return await chat.send_text(textwrap.dedent("""
            Please don't overwork me 😵
            You already have whopping 1️⃣0️⃣ items queued, slow down!
            But know that I'm always glad to help ☺️
        """))

    # Enqueue the task and notify user.
    queue[chat.id].append(url)
    await chat.send_chat_action('upload_photo')

    try:
        picture_path = await loop.run_in_executor(pool, do_screenshot, url)
    except Exception as ex:
        return await chat.send_text('something went wrong 😰')

    caption = f'{url} @ {datetime.utcnow().isoformat()}'
    with open(picture_path, 'rb') as picture:
        await send_picture(chat, picture, caption)

    os.remove(picture_path)


async def send_picture(chat: aiotg.Chat, pic, caption, attempts=5):
    for attempt in range(attempts):
        try:
            await chat.send_document(pic, caption)
        except aiotg.bot.BotApiError:
            await asyncio.sleep(2 ** attempt)
        else:
            break

    else:
        raise Exception(f"Couldn't send a picture after {attempts} attempts")
