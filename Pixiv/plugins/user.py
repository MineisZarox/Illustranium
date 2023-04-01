import json
import requests
from bs4 import BeautifulSoup
from .. import pixiv, pxv, Vars
from telethon import events, Button
from telethon.events import CallbackQuery

from . import *


@pixiv.on(events.InlineQuery(pattern="(\d+)?user(s)?(?:\s|$)([\s\S]*)"))
async def iuser(event):
    user_ = event.query.user_id
    query = "".join(event.text.split(maxsplit=1)[1:])
    offset = event.pattern_match.group(1)
    s = event.pattern_match.group(2)
    if offset:
        offset = int(offset)
    else: offset = 0
    c = offset%30
    offset = offset-c
    if c==0 and offset!=0: c = 30
    elif offset==0: c=1
    c = c-1
    if not query:
        return
    if s: sett = offset
    else: sett = 0 
    if query.isdigit(): users = None
    else: users = await pxv.search_user(query, offset=sett)
    if users:
        if list(users.keys())[0] == "error":
            await pxv.login(refresh_token=Vars.TOKEN)
            users = await pxv.search_user(query, offset=sett)
    if s:
        try:
            img, caption, buttons = await usersResult(users, f"s_{query}:{offset}", user_, offset=offset, uc=c)
        except:
            results = await queryResults(event, query, user_)
            return await event.answer(results)
        try:
            await event.answer([event.builder.photo(img, text=caption, buttons=buttons)])
        except:
            try:
                await event.answer([event.builder.photo(ogiMas(img), text=caption, buttons=buttons)])
            except:
                await event.answer([event.builder.photo("Pixiv/plugins/un.jpg", text=caption, buttons=buttons)])
    else:
        try:
            uid = users['user_previews'][0]['user']['id'] if users else query
        except IndexError:
            return await event.answer("`0 results found of given query`")
        try:
            img, caption, buttons = await queryResults(event, str(uid), user_, user=True, offset=offset, uc=c)
        except:
            results = await queryResults(event, query, user_)
            return await event.answer([event.builder.article(results, text=resylts, buttons=[Button.switch_inline(f"Search again", query=users, same_peer=True)])])
        try:
            await event.answer([event.builder.photo(img, text=caption, buttons=buttons)])
        except:
            try:
                await event.answer([event.builder.photo(ogiMas(img), text=caption, buttons=buttons)])
            except:
                await event.answer([event.builder.photo("Pixiv/plugins/un.jpg", text=caption, buttons=buttons)])


@pixiv.on(events.NewMessage(incoming=True, pattern="/(\d+)?user(s)?(?:\s|$)([\s\S]*)"))
async def user(event):
    user_ = int(event.sender.id)
    query = "".join(event.text.split(maxsplit=1)[1:])
    offset = event.pattern_match.group(1)
    s = event.pattern_match.group(2)
    if offset:
        offset = int(offset)
    else: offset = 0
    c = offset%30
    offset = offset-c
    if c==0 and offset != 0 : c = 30
    elif offset == 0 : c = 1
    c = c-1
    if not query:
        return await event.reply("`Give your words to search pixiv out dummy! ...`")
    eve = await event.reply("`Searching...`")
    if s: sett = offset
    else: sett = 0 
    if query.isdigit(): users = None
    else: users = await pxv.search_user(query, offset=sett)
    if users:
        if list(users.keys())[0] == "error":
            await pxv.login(refresh_token=Vars.TOKEN)
            users = await pxv.search_user(query, offset=sett)
    if s:
        try:
            img, caption, buttons = await usersResult(users, f"s_{query}:{offset}", user_, offset=offset, uc=c)
        except:
            results = await queryResults(event, query, user_)
            return await eve.edit(results)
        try:
            await event.client.send_file(event.chat_id, file=img, caption=caption, buttons=buttons)
        except:
            try:
                await event.client.send_file(event.chat_id, file=ogiMas(img), caption=caption, buttons=buttons)
            except:
                await event.client.send_file(event.chat_id, file="Pixiv/plugins/un.jpg", caption=caption, buttons=buttons)
        await eve.delete()
    else:
        try:
            uid = users['user_previews'][0]['user']['id'] if users else query
        except IndexError:
            return await eve.edit("`0 results found of given query`")
        try:
            img, caption, buttons = await queryResults(event, str(uid), user_, user=True, offset=offset, uc=c)
        except:
            results = await queryResults(event, query, user_)
            return await event.answer(results)
        try:
            await event.client.send_file(event.chat_id, file=img, caption=caption, buttons=buttons)
        except:
            try:
                await event.client.send_file(event.chat_id, file=ogiMas(img), caption=caption, buttons=buttons)
            except:
                await event.client.send_file(event.chat_id, file="Pixiv/plugins/un.jpg", caption=caption, buttons=buttons)
    
        await eve.delete()
            
            
@pixiv.on(CallbackQuery(pattern="nu_(\d+)_(\d+)_(.*)"))
async def nextu(event):
    user_ = int(event.sender_id)
    c = int(event.pattern_match.group(1).decode("UTF-8"))
    user = int(event.pattern_match.group(2).decode("UTF-8"))
    query = event.pattern_match.group(3).decode("UTF-8")
    if user != user_: return await event.answer("Send your own query")
    pc = len(userdict[query])
    cc = c+1
    nc = int(query.split(":")[1])
    cc += nc
    pc += nc
    if c == pc-nc and pc<nc+30: 
        c = 0
        cc = nc+1
    
    if pc in offlist and cc == pc+1:
        result = await pxv.search_user(query.split(":", 1)[0].split("_", 1)[1], offset=pc)
        try:
            img, caption, buttons = await usersResult(result, f'{query.split(":", 1)[0]}:{pc}', user_, offset=pc)
        except Exception as e:
            ok = await usersResult(result, query, user_, offset=pc)
            print(ok)
            return
        try:
            return await event.edit(file=img, text=caption, buttons=buttons)
        except:
            try:
                return await event.edit(file=ogiMas(img), text=caption, buttons=buttons)
            except:
                return await event.edit(file="Pixiv/plugins/un.jpg", text=caption, buttons=buttons)
        
    url = f"https://www.pixiv.net/en/users/{userdict[query][c]['id']}"
    caption = f"""**UserId** - {userdict[query][c]['id']}
**Name** - [{userdict[query][c]['name']}]({url})
**Username** - [{userdict[query][c]['uname']}]({url})
**Followers** - {userdict[query][c]['followers']}
**Illustrations** - {userdict[query][c]['illusn']}"""
    img = userdict[query][c]['pimg']
    
    buttons = [
        [
            Button.inline("Prev", data=f"bu_{c-1}_{user_}_{query}"),
            Button.inline(f"{cc}/{pc}", data="cc"),
            Button.inline("Next", data=f"nu_{c+1}_{user_}_{query}"),
        ],
        [
            Button.inline("Illustraions", data=f"uq_{user_}_{userdict[query][c]['id']}")
        ],
    ]
    try:
        return await event.edit(file=img, text=caption, buttons=buttons)
    except:
        try:
            return await event.edit(file=ogiMas(img), text=caption, buttons=buttons)
        except:
            return await event.edit(file="Pixiv/plugins/un.jpg", text=caption, buttons=buttons)

@pixiv.on(CallbackQuery(pattern="bu_(-?(\d+))_(\d+)_(.*)"))
async def backu(event):
    print('han')
    user_ = int(event.sender_id)
    c = int(event.pattern_match.group(1).decode("UTF-8"))
    user = int(event.pattern_match.group(3).decode("UTF-8"))
    query = event.pattern_match.group(4).decode("UTF-8")
    if user != user_: return await event.answer("Send your own query")
    pc = len(userdict[query])
    cc = c+1
    nc = int(query.split(":")[1])
    cc += nc
    if c == -1:
        pc = nc - 30
    if pc in offlist and cc == nc and nc != 0:
        result = await pxv.search_user(query.split(":", 1)[0].split("_", 1)[1], offset=pc)
        try:
            img, caption, buttons = await usersResult(result, f'{query.split(":", 1)[0]}:{pc}', user_, offset=pc, uc=29)
        except Exception as e:
            ok = await usersResult(result, query, user_, offset=pc)
            print(ok)
            return
        try:
            return await event.edit(file=img, text=caption, buttons=buttons)
        except:
            try:
                return await event.edit(file=ogiMas(img), text=caption, buttons=buttons)
            except:
                return await event.edit(file="Pixiv/plugins/un.jpg", text=caption, buttons=buttons)
    if cc == 0: c = pc-1
    pc += nc
    if cc == 0: return await event.answer("No previous illustration to show Honey.")
    url = f"https://www.pixiv.net/en/users/{userdict[query][c]['id']}"
    caption = f"""**UserId** - {userdict[query][c]['id']}
**Name** - [{userdict[query][c]['name']}]({url})
**Username** - [{userdict[query][c]['uname']}]({url})
**Followers** - {userdict[query][c]['followers']}
**Illustrations** - {userdict[query][c]['illusn']}"""
    img = userdict[query][c]['pimg']
    buttons = [
        [
            Button.inline("Prev", data=f"bu_{c-1}_{user_}_{query}"),
            Button.inline(f"{cc}/{pc}", data="cc"),
            Button.inline("Next", data=f"nu_{c+1}_{user_}_{query}")
        ],
        [
            Button.inline("Illustraions", data=f"uq_{user_}_{userdict[query][c]['id']}")
        ],
    ]
    try:
        return await event.edit(file=img, text=caption, buttons=buttons)
    except:
        try:
            return await event.edit(file=ogiMas(img), text=caption, buttons=buttons)
        except:
            return await event.edit(file="Pixiv/plugins/un.jpg", text=caption, buttons=buttons)
        
        
@pixiv.on(CallbackQuery(pattern="uq_(\d+)_(\d+)"))
async def uq(event):
    user = int(event.pattern_match.group(1).decode("UTF-8"))
    uid = int(event.pattern_match.group(2).decode("UTF-8"))
    
    user_ = int(event.sender_id)
    if user != user_: return await event.answer("Send your own query")
    try:
        img, caption, buttons = await queryResults(event, str(uid), user_, user=True, offset=0)
    except:
        result = await queryResults(event, str(uid), user_, user=True)
        return await event.answer(result)
    try:
        return await event.edit(file=img, text=caption, buttons=buttons)
    except:
        try:
            return await event.edit(file=ogiMas(img), text=caption, buttons=buttons)
        except:
            return await event.edit(file="Pixiv/plugins/un.jpg", text=caption, buttons=buttons)
