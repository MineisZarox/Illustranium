import json
import requests
from bs4 import BeautifulSoup
from .. import pixiv, pxv, Vars
from .query import seadict
from telethon import events, Button
from telethon.events import CallbackQuery

artdict = {}

sudos = list(map(int, (Vars.SUDO_IDS).split(" ")))

def ogiMas(url):
    url = url.replace('original', 'master')
    url = url.replace(url[-4:], f"_master1200.jpg")
    return url

async def queryResults(event, query, user_, offset=0, user=False, uc=0):
    async def getresults(user, query, offset):
        if user:
            if offset == 0:
                results = await pxv.user_illusts(int(query))
                query = f"{query}:{offset}"
            else:
                print('han lol')
                results = await pxv.user_illusts(int(query), offset=offset)
                query = f"{query}:{offset}"
        else:
            if offset == 0:
                results = await pxv.search_illust(query)
                query = f"{query}:{offset}"
            else:
                results = await pxv.search_illust(query, offset=offset)
                query = f"{query}:{offset}"
        return [results, query]
    results, query = await getresults(user, query, offset)
    if list(results.keys())[0] == "error":
        await pxv.login(refresh_token=Vars.TOKEN)
        results, query = await getresults(user, query, offset)
    if len(results['illusts']) == 0: return "`0 results found of given query`"
    c = 0
    cc = uc+offset+1
    seadict[query] = []
    for result in results['illusts']:
        rdict = {}
        pc = result['page_count']
        rdict['id'] = int(result['id'])
        rdict['pc'] = int(pc)
        rdict['title'] = result['title']
        rdict['name'] = result['user']['name']
        rdict['uname'] = result['user']['account']
        rdict['userid'] = result['user']['id']
        rdict['views'] = result['total_view']
        if pc == 1:
            img = result['meta_single_page']['original_image_url']
            rdict['imgs'] = [img]
        else:
            imgs = []
            img = result['meta_pages'][c]['image_urls']['original']
            for i in range(pc):
                imgs.append(result['meta_pages'][i]['image_urls']['original'])
            rdict['imgs'] = imgs
        seadict[query].append(rdict)
    c = uc
    pc = offset
    pc += len(results['illusts'])
    print(c, pc)
    url = f"https://www.pixiv.net/en/artworks/{seadict[query][c]['id']}"
    caption = f"""**Title - **[{seadict[query][c]['title']}]({url})
**By user - **[{seadict[query][c]['name']}](https://www.pixiv.net/en/users/{seadict[query][c]['userid']}) | [{seadict[query][c]['uname']}](https://www.pixiv.net/en/users/{seadict[query][c]['userid']})
**Page count** - `{seadict[query][c]['pc']}`
**Views** - `{seadict[query][c]['views']}`"""
    print(type(query), query)
    img = seadict[query][c]['imgs']
    if type(img) is list: img = img[0]
    buttons = [
        [
            Button.inline("Prev", data=f"bq_{c-1}_{user_}_{query}"),
            Button.inline(f"{cc}/{pc}", data="cc"),
            Button.inline("Next", data=f"nq_{c+1}_{user_}_{query}")
        ],
        [
            Button.inline("Get In", data=f"q_{c}_{user_}_{seadict[query][c]['id']}_{query}")
        ],
    ]
    return [img, caption, buttons]
  
async def illustResult(artId, user):
    url = f"https://www.pixiv.net/en/artworks/{artId}"
    results = await pxv.illust_detail(artId)
    if list(results.keys())[0] == "error":
        await pxv.login(refresh_token=Vars.TOKEN)
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
        ]
    ]
    return [img, caption, buttons]

@pixiv.on(events.InlineQuery)
async def pixivi(event):
    user_ = event.query.user_id
    artId = ""
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
        return
    if "limit_" in img: return await event.answer([event.builder.article(title="FORBIDDEN")])
    try:
        await event.answer([event.builder.photo(img, text=caption, buttons=buttons)])
    except:
        try:
            await event.answer([event.builder.photo(ogiMas(img), text=caption, buttons=buttons)])
        except:
            await event.answer([event.builder.photo("Pixiv/plugins/un.jpg", text=caption, buttons=buttons)])
    
            
            
@pixiv.on(CallbackQuery(pattern="cc"))
async def cc(event):
    return await event.answer("Hmm")

@pixiv.on(CallbackQuery(pattern="b_(\d+)_(\d+)_(\d+)_(.*)"))
async def back(event):
    user_ = int(event.sender_id)
    c = int(event.pattern_match.group(1).decode("UTF-8"))
    pc = int(event.pattern_match.group(2).decode("UTF-8"))
    user = int(event.pattern_match.group(3).decode("UTF-8"))
    artId = int(event.pattern_match.group(4).decode("UTF-8"))
    if user != user_: return await event.answer("Send your own query")
    
    if c == 0: c = pc
    
    img = artdict[artId][c-1]
    
    buttons = [
        [
            Button.inline("Prev", data=f"b_{c-1}_{pc}_{user_}_{artId}"),
            Button.inline(f"{c}/{pc}", data=f"cc"),
            Button.inline("Next", data=f"n_{c+1}_{pc}_{user_}_{artId}")
        ],
        [
            Button.inline("Download", data=f"d_{c-1}_{pc}_{user_}_{artId}")
        ]
    ]
    eve = await event.get_message()
    if eve:
        if len(eve.buttons) == 3: buttons.append([Button.inline("Get out", data=str(eve.buttons[2][0].data)[2:-1])])

    try:
        return await event.edit(file=img, buttons=buttons)
    except Exception as ee:
        print(ee)
        try:
            return await event.edit(file=ogiMas(img), buttons=buttons)
        except Exception as ee:
            print(ee)
            return await event.edit(file="Pixiv/plugins/un.jpg", buttons=buttons)

@pixiv.on(CallbackQuery(pattern="n_(\d+)_(\d+)_(\d+)_(.*)"))
async def next(event):
    user_ = int(event.sender_id)
    c = int(event.pattern_match.group(1).decode("UTF-8"))
    pc = int(event.pattern_match.group(2).decode("UTF-8"))
    user = int(event.pattern_match.group(3).decode("UTF-8"))
    artId = int(event.pattern_match.group(4).decode("UTF-8"))
    if user != user_: return await event.answer("Send your own query")
    if c == pc+1: c = 1
    img = artdict[artId][c-1]
    
    buttons = [
        [
            Button.inline("Prev", data=f"b_{c-1}_{pc}_{user_}_{artId}"),
            Button.inline(f"{c}/{pc}", data=f"cc"),
            Button.inline("Next", data=f"n_{c+1}_{pc}_{user_}_{artId}")
        ],
        [
            Button.inline("Download", data=f"d_{c-1}_{pc}_{user_}_{artId}")
        ]
    ]
    eve = await event.get_message()
    if eve: 
        if len(eve.buttons) == 3: buttons.append([Button.inline("Get out", data=str(eve.buttons[2][0].data)[2:-1])])
        elif eve.buttons[0][0].text == "Return": buttons.append([Button.inline("Get out", data=str(eve.buttons[1][0].data)[2:-1])])
    try:
        return await event.edit(file=img, buttons=buttons)
    except Exception as ee:
        print(ee)
        try:
            return await event.edit(file=ogiMas(img), buttons=buttons)
        except Exception as ee:
            print(ee)
            return await event.edit(file="Pixiv/plugins/un.jpg", buttons=buttons)

    
@pixiv.on(CallbackQuery(pattern="d_(\d+)_(\d+)_(\d+)_(.*)"))
async def download(event):
    user_ = int(event.sender_id)
    c = int(event.pattern_match.group(1).decode("UTF-8"))
    pc = int(event.pattern_match.group(2).decode("UTF-8"))
    user = int(event.pattern_match.group(3).decode("UTF-8"))
    artId = int(event.pattern_match.group(4).decode("UTF-8"))
    if user != user_: return await event.answer("Send your own query")
    
    img = artdict[artId][c]
    buttons = [[Button.inline("Return", data=f"n_{c+1}_{pc}_{user_}_{artId}")],]
    
    eve = await event.get_message()
    if eve:
        if len(eve.buttons) == 3: buttons.append([Button.inline("Get out", data=str(eve.buttons[2][0].data)[2:-1])])
    try:
        return await event.edit(file=img, force_document=True, buttons=buttons)
    except Exception as e:
        print(e)
        try:
            return await event.edit(file=ogiMas(img), force_document=True, buttons=buttons)
        except Exception as ee:
            print(ee)
            return await event.edit(file="Pixiv/plugins/un.jpg", force_document=True, buttons=buttons)
        
        
