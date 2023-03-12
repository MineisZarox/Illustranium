from .. import pixiv, Vars
from telethon import Button

async def startup():
    await pixiv.send_message(Vars.LOG_GRP, "**Pixiv has been started successfully.**", buttons=[(Button.url("Shinichi", "https://t.me/catuserbotot"),)],)
