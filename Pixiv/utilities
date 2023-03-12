from telethon.sync import events
from .. import Vars
from telethon.tl.types import ChannelParticipantsAdmins

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

def check_owner(func):
    async def wrapper(event: events):
        user = event.sender.id
        owner = int(Vars.OWNER_ID)
        if user != owner: return
        else: await func(event)
    return wrapper

def check_admin(func):
    async def wrapper(event: events):
        admins = []
        iris = event.sender.id
        admins.append(int(Vars.OWNER_ID))
        async for user in event.client.iter_participants(event.chat_id, filter=ChannelParticipantsAdmins):
            admins.append(user.id)
        if iris not in admins: return await event.reply("Only admins can use this command and you are not of them.")
        else: await func(event)
    return wrapper

def check_blocked(func):
    async def wrapper(event: events):
        chat = event.chat_id
        list = []
        ids = int(Vars.BLOCKED_CHAT).split(' ')
        for id in ids:
            list.append(int(id))
        if chat not in list: return await event.reply("This function cant be used for the given group. You can ask further queries in support group")
        else: await func(event)
    return wrapper
