
from datetime import datetime
from telethon import events, Button
from .. import pixiv, Vars

from telethon.events import CallbackQuery

sudos = list(map(int, (Vars.SUDO_IDS).split(" ")))

    
@pixiv.on(events.NewMessage(incoming=True, pattern=f"^/start({Vars.BOT_USERNAME})$"))
async def start(event):
    user = await pixiv.get_entity(int(event.sender.id))
    if event.is_group: await event.reply(
        f"Hi {user.first_name} 👋[\u200d](https://telegra.ph/file/2a10282c49d4c10847971.jpg)\nGet illustration from pixiv.net using Illustranium\n\nSend /help to check out cmds and how to use illustranium",
        buttons=[[Button.url("Dev", "https://t.me/zarox")], [Button.url("Update", "https://t.me/update")]],
        link_preview=True
    )

        
@pixiv.on(events.NewMessage(incoming=True, pattern=f"^/help({Vars.BOT_USERNAME})$"))
async def help(event):
    
    user = event.sender.id
    if event.is_group: await event.reply(
        f"""__Send pixiv illust link or use cmds 

/pixiv <artid \ search query>
/user <userid \ username>
/users <search user>

Example:

/pixiv 102944326
/pixiv nature

/user 49552835
/user wlop
/users snake

For any concern, appreciation or suggestion contact__ @Zarox""",
        buttons=[Button.inline("Inline", data=f"inline_{user}")]
    )


        
@pixiv.on(events.NewMessage(incoming=True, pattern=f"^/help({Vars.BOT_USERNAME})?$"))
async def help(event):
    user = event.sender.id
    if event.is_private: await event.reply(
        f"""__Send pixiv illust link or use cmds 

/pixiv <artid \ search query>
/user <userid \ username>
/users <search user>

Example:

/pixiv 102944326
/pixiv nature

/user 49552835
/user wlop
/users snake

For any concern, appreciation or suggestion contact__ @Zarox""",
        buttons=[Button.inline("Inline", data=f"inline_{user}")]
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
        buttons=[[Button.url("Dev", "https://t.me/zarox")], [Button.url("Update", "https://t.me/update")]],
        link_preview=True)


@pixiv.on(CallbackQuery(pattern="inline_(\d+)"))
async def inline(event):
    user_ = int(event.sender_id)
    user = int(event.pattern_match.group(1).decode("UTF-8"))
    if user != user_: return
    text = """__Send pixiv illust link or use cmds 
 
 @PixivArtbot pixiv <artid \ search query>
 @PixivArtbot user <userid \ username>
 @PixivArtbot users <search user>
 
 Example:
 
 @PixivArtbot pixiv 102944326
 @PixivArtbot pixiv nature
 
 @PixivArtbot user 49552835
 @PixivArtbot user wlop
 @PixivArtbot users snake
 
 For any concern, appreciation or suggestion contact__ @Zarox"""
    await event.edit(text,
    buttons=[Button.inline("Commands", data=f"cg_{user}")]
    )
    
@pixiv.on(CallbackQuery(pattern="cg_(\d+)"))
async def cg(event):
    user_ = int(event.sender_id)
    user = int(event.pattern_match.group(1).decode("UTF-8"))
    if user != user_: return
    eve = await event.get_message()
    text = """__Send pixiv illust link or use cmds 

/pixiv <artid \ search query>
/user <userid \ username>
/users <search user>

Example:

/pixiv 102944326
/pixiv nature

/user 49552835
/user wlop
/users snake

For any concern, appreciation or suggestion contact__ @Zarox"""
    await event.edit(text,
    buttons=[Button.inline("Inline", data=f"inline_{user}")]
    )
    
@pixiv.on(events.NewMessage(incoming=True))
async def copypaste(event):
    user_ = int(event.sender_id)
    if user_ != Vars.OWNER_ID and event.is_private:
          await event.forward_to(Vars.OWNER_ID)