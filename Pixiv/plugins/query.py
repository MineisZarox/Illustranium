import json
import requests
from bs4 import BeautifulSoup

from .. import pixiv, pxv, Vars
from telethon import events, Button
from telethon.events import CallbackQuery

from . import *

sudos = list(map(int, (Vars.SUDO_IDS).split(" ")))


@pixiv.on(events.InlineQuery(pattern="pixiv(\d+)?(?:\s|$)([\s\S]*)"))
async def iqueryi(event):
    user_ = event.query.user_id
    if event.text.startswith("https://www.pixiv.net/en/artworks"):
        artId = (event.text).split("/")[-1]
        artId = artId.split(" ")[0]
        try: 
            artId = int(artId)
        except:
            return
        img, caption, buttons = await illustResult(int(artId), user_)
    elif event.text.startswith("https://www.pixiv.net/en/users"):
        artId = (event.text).split("/")[-1]
        artId = artId.split(" ")[0]
        try: 
            artId = int(artId)
        except:
            return
        img, caption, buttons = await queryResults(event, int(artId), user_, user=True)
    else:
        query = event.text
        if not query: return
        try:
            if query.isdigit(): img, caption, buttons = await illustResult(int(query), user_)
            else: img, caption, buttons = await queryResults(event, query, user_,)
        except:
            results = await queryResults(event, query, user_)
            return await event.answer(results)
    if "limit_" in img: return await event.answer([event.builder.article(title="FORBIDDEN")])
    try:
        await event.answer([event.builder.photo(img, text=caption, buttons=buttons)])
    except:
        try:
            await event.answer([event.builder.photo(ogiMas(img), text=caption, buttons=buttons)])
        except:
            await event.answer([event.builder.photo("Pixiv/plugins/un.jpg", text=caption, buttons=buttons)])

@pixiv.on(events.NewMessage(incoming=True))  
async def link(event):
    user_ = int(event.sender.id)
    if event.text.startswith("https://www.pixiv.net/en/artworks"):
        artId = (event.text).split("/")[-1]
        artId = artId.split(" ")[0]
        eve = await event.reply("`Processing...`")
        img, caption, buttons = await illustResult(int(artId), user_)
        if "limit_" in img: return await eve.edit("FORBIDDEN")
        await eve.delete()
    elif event.text.startswith("https://www.pixiv.net/en/users"):
        artId = (event.text).split("/")[-1]
        artId = artId.split(" ")[0]
        eve = await event.reply("`Processing...`")
        img, caption, buttons = await queryResults(event, int(artId), user_, user=True)
        if "limit_" in img: return await eve.edit("FORBIDDEN")
        await eve.delete()
    
    
        offset = (event.text.split(" ", 1)[0]).split("pixiv")[1]
        query = event.text.split(" ", 1)[1]
    else:
        if event.text.startswith("/pixiv") and event.is_group:
            offset = (event.text.split(" ", 1)[0]).split("pixiv")[1]
            query = event.text.split(" ", 1)[1]
        else:
            offset = 0
            query = event.text
        if query.startswith("/"): return
        if offset != "": offset = int(offset)
        else: offset = 0
        c = offset%30
        offset = offset-c
        if c==0 and offset!=0: c = 30
        elif offset==0: c=1
        c = c-1
        if not query:
            return await event.reply("`Give your words to search pixiv out dummy! ...`")
        eve = await event.reply("`Searching...`")
        
        try:
            if query.isdigit(): img, caption, buttons = await illustResult(int(query), user_)
            else: img, caption, buttons = await queryResults(event, query, user_, offset=offset, uc=c)
        except Exception as e:
            print(e)
            result = await queryResults(event, query, user_, offset=offset)
            return await eve.edit(result)
        if "limit_" in img: return await eve.edit("FORBIDDEN")
        await eve.delete()

    try:
        return await event.client.send_file(event.chat_id, file=img, caption=caption, buttons=buttons)
    except:
        try:
            return await event.client.send_file(event.chat_id, file=ogiMas(img), caption=caption, buttons=buttons)
        except:
            return await event.client.send_file(event.chat_id, file="Pixiv/plugins/un.jpg", caption=caption, buttons=buttons)


@pixiv.on(CallbackQuery(pattern="nq_(\d+)_(\d+)_(.*)"))
async def nextq(event):
    print("yessss")
    user_ = int(event.sender_id)
    c = int(event.pattern_match.group(1).decode("UTF-8"))
    user = int(event.pattern_match.group(2).decode("UTF-8"))
    query = event.pattern_match.group(3).decode("UTF-8")
    if user != user_: return await event.answer("Send your own query")
    pc = len(seadict[query])
    cc = c+1
    nc = 0
    
    if ":" in query:
        query, nc = query.split(":")
        nc = int(nc)
    cc += nc
    pc += nc
    if c == pc-nc and pc<nc+30: 
        c = 0
        cc = nc+1
    if pc in offlist and cc == pc+1:
        if query.isdigit():
            try:
                img, caption, buttons = await queryResults(event, query, user_, user=True, offset=pc)
            except Exception as e:
                return print(e)
        else:
            try:
                img, caption, buttons = await queryResults(event, query, user_, offset=pc)
            except Exception as e:
                return print(e)
        try:
            return await event.edit(file=img, text=caption, buttons=buttons)
        except:
            try:
                return await event.edit(file=ogiMas(img), text=caption, buttons=buttons)
            except:
                return await event.edit(file="Pixiv/plugins/un.jpg", text=caption, buttons=buttons)
    else:
        pass
    query = f"{query}:{nc}"
    url = f"https://www.pixiv.net/en/artworks/{seadict[query][c]['id']}"
    caption = f"""**Title - **[{seadict[query][c]['title']}]({url})
**By user - **[{seadict[query][c]['name']}](https://www.pixiv.net/en/users/{seadict[query][c]['userid']}) | [{seadict[query][c]['uname']}](https://www.pixiv.net/en/users/{seadict[query][c]['userid']})
**Page count** - `{seadict[query][c]['pc']}`
**Views** - `{seadict[query][c]['views']}`"""
    img = seadict[query][c]['imgs']
    if type(img) is list: img = img[0]
    buttons = [
        [
            Button.inline("Prev", data=f"bq_{c-1}_{user}_{query}"),
            Button.inline(f"{cc}/{pc}", data="cc"),
            Button.inline("Next", data=f"nq_{c+1}_{user}_{query}")
        ],
        [
            Button.inline("Get In", data=f"q_{c}_{user}_{seadict[query][c]['id']}_{query}")
        ],
    ]
    try:
        return await event.edit(file=img, text=caption, buttons=buttons)
    except:
        try:
            return await event.edit(file=ogiMas(img), text=caption, buttons=buttons)
        except:
            return await event.edit(file="Pixiv/plugins/un.jpg", text=caption, buttons=buttons)

        
@pixiv.on(CallbackQuery(pattern="bq_(-?(\d+))_(\d+)_(.*)"))
async def backq(event):
    print("han back ")
    user_ = int(event.sender_id)
    c = int(event.pattern_match.group(1).decode("UTF-8"))
    user = int(event.pattern_match.group(3).decode("UTF-8"))
    query = event.pattern_match.group(4).decode("UTF-8")
    if user != user_: return await event.answer("Send your own query")
    pc = len(seadict[query])
    cc = c+1
    nc = 0
    if ":" in query:
        query, nc = query.split(":")
        nc = int(nc)
    if c == -1 and nc != 0:
        pc = nc - 30
    cc += nc
    print("out", c, cc, pc, nc)
    if pc in offlist and cc == nc and nc != 0:
        print("In", c, cc, pc, nc)
        if query.isdigit():
            img, caption, buttons = await queryResults(event, query, user_, user=True, offset=pc, uc=29)
            # try:
            #     img, caption, buttons = await queryResults(event, query, user_, user=True, offset=pc, c=cc-1)
            # except Exception as e:
            #     return print(e)
        else:
            try:
                img, caption, buttons = await queryResults(event, query, user_, offset=pc, uc=29)
            except Exception as e:
                return print(e)
        try:
            return await event.edit(file=img, text=caption, buttons=buttons)
        except:
            try:
                return await event.edit(file=ogiMas(img), text=caption, buttons=buttons)
            except:
                return await event.edit(file="Pixiv/plugins/un.jpg", text=caption, buttons=buttons)
    else:
        pass
    if cc == 0: c = pc-1
    query = f"{query}:{nc}"
    pc += nc
    if cc == 0: return await event.answer("No previous illustration to show Honey.")
    url = f"https://www.pixiv.net/en/artworks/{seadict[query][c]['id']}"
    caption = f"""**Title - **[{seadict[query][c]['title']}]({url})
**By user - **[{seadict[query][c]['name']}](https://www.pixiv.net/en/users/{seadict[query][c]['userid']}) | [{seadict[query][c]['uname']}](https://www.pixiv.net/en/users/{seadict[query][c]['userid']})
**Page count** - `{seadict[query][c]['pc']}`
**Views** - `{seadict[query][c]['views']}`"""
    img = seadict[query][c]['imgs']
    if type(img) is list: img = img[0]
        
    buttons = [
        [
            Button.inline("Prev", data=f"bq_{c-1}_{user}_{query}"),
            Button.inline(f"{cc}/{pc}", data="cc"),
            Button.inline("Next", data=f"nq_{c+1}_{user}_{query}")
        ],
        [
            Button.inline("Get In", data=f"q_{c}_{user}_{seadict[query][c]['id']}_{query}")
        ],
    ]
    try:
        return await event.edit(file=img, text=caption, buttons=buttons)
    except:
        try:
            return await event.edit(file=ogiMas(img), text=caption, buttons=buttons)
        except:
            return await event.edit(file="Pixiv/plugins/un.jpg", text=caption, buttons=buttons)
        
        
    
            
@pixiv.on(CallbackQuery(pattern="q_(\d+)_(\d+)_(\d+)_(.*)"))
async def qi(event):
    user_ = int(event.sender_id)
    qc = int(event.pattern_match.group(1).decode("UTF-8"))
    user = int(event.pattern_match.group(2).decode("UTF-8"))
    artId = int(event.pattern_match.group(3).decode("UTF-8"))
    query = event.pattern_match.group(4).decode("UTF-8")
    print(user, user_)
    if user != user_: return await event.answer("Send your own query")
    
    url = f"https://www.pixiv.net/en/artworks/{artId}"
    results = await pxv.illust_detail(artId)
    caption = f"""**Title - **[{results['illust']['title']}]({url})
**By user - **[{results['illust']['user']['name']}](https://www.pixiv.net/en/users/{results['illust']['user']['id']}) | [{results['illust']['user']['account']}](https://www.pixiv.net/en/users/{results['illust']['user']['id']})
**Views - **`{results['illust']['total_view']}`"""
    pc = results['illust']['page_count']
    c = 0
    cc = 1
    img = ""
    if pc == 1:
        img = results['illust']['meta_single_page']['original_image_url']
        artdict[artId] = [img]
    else:
        img = results['illust']['meta_pages'][c]['image_urls']['original']
        imgs = []
        for i in range(pc):
            imgs.append(results['illust']['meta_pages'][i]['image_urls']['original'])
        artdict[artId] = imgs
    
    buttons = [
        [
            Button.inline("Prev", data=f"b_{0}_{pc}_{user}_{artId}"),
            Button.inline(f"{cc}/{pc}", data="cc"),
            Button.inline("Next", data=f"n_{cc+1}_{pc}_{user}_{artId}")
        ],
        [
            Button.inline("Download", data=f"d_{c}_{pc}_{user}_{artId}")
        ],
        [
            Button.inline("Get out", data=f"nq_{qc}_{user}_{query}")
        ]
    ]
    
    try:
        return await event.edit(file=img, text=caption, buttons=buttons)
    except Exception as e:
        print(e)
        try:
            return await event.edit(file=ogiMas(img), text=caption, buttons=buttons)
        except:
            return await event.edit(file="Pixiv/plugins/un.jpg", text=caption, buttons=buttons)

