import json
import requests
from bs4 import BeautifulSoup

from .. import pixiv, pxv, Vars
from telethon import events, Button
from telethon.events import CallbackQuery


sudos = list(map(int, (Vars.SUDO_IDS).split(" ")))

artdict  = {}
seadict = {}

offlist = [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360, 390, 420, 450, 480, 510, 540, 570, 600, 630, 660, 690, 720, 750, 780, 810, 840, 870, 900, 930, 960, 990, 1020, 1050, 1080, 1110, 1140, 1170, 1200, 1230, 1260, 1290, 1320, 1350, 1380, 1410, 1440, 1470, 1500, 1530, 1560, 1590, 1620, 1650, 1680, 1710, 1740, 1770, 1800, 1830, 1860, 1890, 1920, 1950, 1980, 2010, 2040, 2070, 2100, 2130, 2160, 2190, 2220, 2250, 2280, 2310, 2340, 2370, 2400, 2430, 2460, 2490, 2520, 2550, 2580, 2610, 2640, 2670, 2700, 2730, 2760, 2790, 2820, 2850, 2880, 2910, 2940, 2970]

async def isfloat(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

def ogiMas(url):
    url = url.replace('original', 'master')
    url = url.replace(url[-4:], f"_master1200.jpg")
    return url

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
    

async def usersResult(results, query, user_, offset=0, uc=0):
    c = 0
    cc = uc+1+offset
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
    c = uc
    pc += offset
    
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


async def usersResult(results, query, user_, offset=0, uc=0):
    c = 0
    cc = uc+1+offset
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
    c = uc
    pc += offset
    
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

