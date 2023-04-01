
from datetime import datetime
from telethon import events, Button
from .. import pixiv, Vars

from telethon.events import CallbackQuery

sudos = list(map(int, (Vars.SUDO_IDS).split(" ")))

text = f"""__[Pixiv](https://www.pixiv.net/en/) is a Japanese online community for artists. Using illustranium you can get illustrations from pixiv.net
Just directly send me your search query or send direct link to post
Also you can get all illustrations of the user by- 
/user <userid \ username>

Or can even search for multiple users
/users <search user>

Example:
/user 49552835
/user wlop
/users snake

To search illustration in groups use /pixiv command - 
/pixiv nezuko

Note - Dont think the search results are limited to 30 you can go further till the end of result

For any concern, appreciation or suggestion contact__ @Zarox"""
    
@pixiv.on(events.NewMessage(incoming=True, pattern=f"^/start({Vars.BOT_USERNAME})$"))
async def start(event):
    user = await pixiv.get_entity(int(event.sender.id))
    if event.is_group: await event.reply(
        f"Hi {user.first_name} 👋[\u200d](https://telegra.ph/file/2a10282c49d4c10847971.jpg)\nGet illustration from pixiv.net using Illustranium\n\nSend /help to check out cmds and how to use illustranium",
        buttons=[[Button.url("Dev", "https://t.me/zarox")], [Button.url("Update", "https://t.me/zaroxverse")]],
        link_preview=True
    )

        
@pixiv.on(events.NewMessage(incoming=True, pattern=f"^/help({Vars.BOT_USERNAME})$"))
async def help(event):
    
    user = event.sender.id
    if event.is_group: await event.reply(
        text,
        buttons=[Button.inline("Inline", data=f"inline_{user}")],
        link_preview=False
    )


        
@pixiv.on(events.NewMessage(incoming=True, pattern=f"^/help({Vars.BOT_USERNAME})?$"))
async def help(event):
    user = event.sender.id
    if event.is_private: await event.reply(
        text,
        buttons=[Button.inline("Inline", data=f"inline_{user}")],
        link_preview=False
    )
        

@pixiv.on(events.NewMessage(incoming=True, pattern=f"^/ping({Vars.BOT_USERNAME})?$"))
async def ping(event):
    user = await pixiv.get_entity(int(event.sender.id))
    if user.id not in sudos:
        return
    start = datetime.now()
    ping = await event.reply("ᴘɪɴɢ")
    end = datetime.now()
    ms = (end - start).microseconds / 1000
    await ping.edit(f"ᴘɪɴɢ :`{ms} ms`")
    
    

    
@pixiv.on(events.NewMessage(incoming=True,  pattern=f"^/start({Vars.BOT_USERNAME})? ?(.*)?$"))
async def start(event):
    user = await pixiv.get_entity(int(event.sender.id))
    web = event.pattern_match.group(2)
    print(web)
    startm = f"#START\n**User**: [{user.first_name}](tg://user?id={user.id})\n**Username**: @{user.username}\n**ID**: {user.id}"
    if event.is_private:
        if web and web == "web":
            startm += "\n\n**From Web**"
        await pixiv.send_message(int(Vars.OWNER_ID), startm)
        await event.reply(
        f"Hi {user.first_name} 👋[\u200d](https://telegra.ph/file/2a10282c49d4c10847971.jpg)\nGet illustration from pixiv.net using Illustranium\n\nSend /help to check out cmds and how to use illustranium",
        buttons=[[Button.url("Dev", "https://t.me/zarox")], [Button.url("Update", "https://t.me/zaroxverse")]],
        link_preview=True)


@pixiv.on(CallbackQuery(pattern="inline_(\d+)"))
async def inline(event):
    user_ = int(event.sender_id)
    user = int(event.pattern_match.group(1).decode("UTF-8"))
    if user != user_: return
    text = f"""__[Pixiv](https://www.pixiv.net/en/) is a Japanese online community for artists. Using illustranium you can get illustrations from pixiv.net
Just directly type your search query or use direct link to post - 
@PixivartBot nezuko

Also you can get all illustrations of the user by- 
@PixivartBot user <userid \ username>

Or can even search for multiple users - 
@PixivartBot users <search user>

Example:
@PixivartBotuser 49552835
@PixivartBotuser wlop
@PixivartBotusers snake

Note - Dont think the search results are limited to 30 you can go further till the end of result

For any concern, appreciation or suggestion contact__ @Zarox"""
    await event.edit(
        text,
        buttons=[Button.inline("Commands", data=f"cg_{user}")],
        link_preview=False
    )
    
@pixiv.on(CallbackQuery(pattern="cg_(\d+)"))
async def cg(event):
    user_ = int(event.sender_id)
    user = int(event.pattern_match.group(1).decode("UTF-8"))
    if user != user_: return
    eve = await event.get_message()
    
    await event.edit(
        text,
        buttons=[Button.inline("Inline", data=f"inline_{user}")],
        link_preview=False
    )
    
@pixiv.on(events.NewMessage(incoming=True))
async def copypaste(event):
    user_ = int(event.sender_id)
    if user_ != Vars.OWNER_ID and event.is_private:
          await event.forward_to(Vars.OWNER_ID)
