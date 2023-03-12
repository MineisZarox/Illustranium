import json
import requests
from bs4 import BeautifulSoup
from .. import pixiv, pxv, Vars
from telethon import events, Button
from telethon.events import CallbackQuery
from .query import queryResults, seadict as userdict

sudos = list(map(int, (Vars.SUDO_IDS).split(" ")))

def ogiMas(url):
    url = url.replace('original', 'master')
    url = url.replace(url[-4:], f"_master1200.jpg")
    return url

async def usersResult(results, query, user_, offset=0):
    c = 0
    cc = 1
    userdict[query] = []
    for result in results['user_previews']:
        rdict = {}
        uid = result['user']['id']
        details = await pxv.user_detail(uid)
        rdict['id'] = details['user']['id']
        rdict['name'] = details['user']['name']
        rdict['uname'] = details['user']['account']
        rdict['followers'] = details['profile']['total_follow_users']
        rdict['illusn'] = details['profile']['total_illusts']
        rdict['pimg'] = details['profile']['background_image_url'] if details['profile']['background_image_url'] else details['user']['profile_image_urls']['medium']
        userdict[query].append(rdict)
    pc = len(results['user_previews'])
    if len(results['user_previews']) == 0: return "`0 results found of given query`"

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
    return [img, caption, buttons]



@pixiv.on(events.InlineQuery(pattern="(\d+)?user(s)?(?:\s|$)([\s\S]*)"))
async def iuser(event):
    user_ = event.query.user_id
    offset = event.pattern_match.group(1)
    query = "".join(event.text.split(maxsplit=1)[1:])
    s = event.pattern_match.group(2)
    if offset:
        offset = int(offset.decode("UTF-8"))
    else: offset = 0
    if query.isdigit(): users = None
    else: users = await pxv.search_user(query)
    if users:
        if list(users.keys())[0] == "error":
            await pxv.login(refresh_token=Vars.TOKEN)
            users = await pxv.search_user(query)
    if s:
        try:
            img, caption, buttons = await usersResult(users, f"s_{query}", user_, offset=offset)
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
            return await eve.edit("`0 results found of given query`")
        try:
            img, caption, buttons = await queryResults(event, str(uid), user_, user=True, offset=offset)
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


@pixiv.on(events.NewMessage(incoming=True, pattern="/(\d+)?user(s)?(?:\s|$)([\s\S]*)"))
async def user(event):
    user_ = int(event.sender.id)
    query = "".join(event.message.message.split(maxsplit=1)[1:])
    offset = event.pattern_match.group(1)
    s = event.pattern_match.group(2)
    if offset:
        offset = int(offset)
    else: offset = 0
    if not query:
        return await event.reply("`Give your words to search pixiv out dummy! ...`")
    eve = await event.reply("`Searching...`")
    if query.isdigit(): users = None
    else: users = await pxv.search_user(query)
    
    if s:
        try:
            img, caption, buttons = await usersResult(users, f"s_{query}", user_, offset=offset)
        except:
            result = await usersResult(users, f"s_{query}", user_, offset=offset)
            return await eve.edit(result)
        try:
            await event.client.send_file(event.chat_id, file=img, caption=caption, buttons=buttons)
        except:
            try:
                await event.client.send_file(event.chat_id, file=ogiMas(img), caption=caption, buttons=buttons)
            except:
                await event.client.send_file(event.chat_id, file="Pixiv/plugins/un.jpg", caption=caption, buttons=buttons)

    else:
        try:
            uid = users['user_previews'][0]['user']['id'] if users else query
        except IndexError:
            return await eve.edit("`0 results found of given query`")
        try:
            img, caption, buttons = await queryResults(event, str(uid), user_, user=True, offset=offset)
        except:
            result = await queryResults(event, str(uid), user_, user=True, offset=offset)
            return await eve.edit(result)
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
    if c == pc: c = 0
    cc = c+1
    
    url = f"https://www.pixiv.net/en/users/{userdict[query][c]['id']}"
    caption = f"""**UserId** - {userdict[query][c]['id']}
**Name** - [{userdict[query][c]['name']}]({url})
**Username** - [{userdict[query][c]['uname']}]({url})
**Followers** - {userdict[query][c]['followers']}
**Illustrations** - {userdict[query][c]['illusn']}"""
    img = userdict[query][c]['pimg']
    
    print(img)
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
    print(c, pc)
    if c == -1: c = pc-1
    cc = c+1    
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
    print(user, user_)
    if user != user_: return await event.answer("Send your own query")
    results = await pxv.user_illusts(uid)
    uid = str(uid)
    query = str(uid)
    query = uid
    c = 0
    cc = 1
    userdict[uid] = []
    for result in results['illusts']:
        rdict = {}
        pc = result['page_count']
        rdict['id'] = int(result['id'])
        rdict['pc'] = int(pc)
        rdict['title'] = result['title']
        rdict['name'] = result['user']['name']
        rdict['userid'] = result['user']['id']
        if pc == 1:
            img = result['meta_single_page']['original_image_url']
            rdict['imgs'] = [img]
        else:
            imgs = []
            img = result['meta_pages'][c]['image_urls']['original']
            for i in range(pc):
                imgs.append(result['meta_pages'][i]['image_urls']['original'])
            rdict['imgs'] = imgs
        userdict[uid].append(rdict)

    pc = len(results['illusts'])
    url = f"https://www.pixiv.net/en/users/{userdict[query][c]['id']}"
    caption = f"""**Title - **[{userdict[query][c]['title']}]({url})
**By user - **[{userdict[query][c]['name']}](https://www.pixiv.net/en/users/{userdict[query][c]['userid']})
**Page count** - `{userdict[query][c]['pc']}`"""
    img = userdict[query][c]['imgs']
    if type(img) is list: img = img[0]
    buttons = [
        [
            Button.inline("Prev", data=f"bq_{0}_{user_}_{uid}"),
            Button.inline(f"{cc}/{pc}", data="cc"),
            Button.inline("Next", data=f"nq_{c+1}_{user_}_{uid}")
        ],
        [
            Button.inline("Get In", data=f"q_{c}_{user_}_{userdict[query][c]['id']}_{uid}")
        ],
    ]
    try:
        return await event.edit(file=img, text=caption, buttons=buttons)
    except:
        try:
            return await event.edit(file=ogiMas(img), text=caption, buttons=buttons)
        except:
            return await event.edit(file="Pixiv/plugins/un.jpg", text=caption, buttons=buttons)
