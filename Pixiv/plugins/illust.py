import json
import requests
from bs4 import BeautifulSoup
from .. import pixiv, pxv, Vars

from telethon import events, Button
from telethon.events import CallbackQuery

sudos = list(map(int, (Vars.SUDO_IDS).split(" ")))

from . import *


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
        
        
