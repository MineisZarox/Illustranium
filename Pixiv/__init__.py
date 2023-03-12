import os
import logging
from telethon import TelegramClient
from telethon.network.connection.tcpabridged import ConnectionTcpAbridged
from config import chivar as Vars
from telethon import events
from pixivpy_async import *

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)


pixiv = TelegramClient(
        "pixiv",
        api_id=Vars.API_ID,
        api_hash=Vars.API_HASH,
        connection=ConnectionTcpAbridged,
        auto_reconnect=True,
        connection_retries=None,
    ).start(bot_token=Vars.BOT_TOKEN)


client = PixivClient().start()
pxv = AppPixivAPI(client=client)

def auth_(user):
    authorized = []
    authorized.append(int(Vars.OWNER_ID))
    ids = Vars.SUDO_IDS.split(' ')
    for id in ids:
        authorized.append(int(id))
    return authorized

def check_auth(func):
    async def wrapper(event: events):
        user = event.sender.id
        auth = auth_(user)
        if user not in auth: return
        else: await func(event)
    return wrapper
