import asyncio
from . import pixiv, pxv, client, Vars
from .utilities.utility import load_plugins
from .utilities.startup import startup


RT = Vars.TOKEN
    
async def initiation():
    load_plugins("plugins")
    await pxv.login(refresh_token=RT) 
    print("Pixiv Deployed Successfully!")
    return

pixiv.loop.run_until_complete(initiation())

if __name__ == "__main__":
    pixiv.run_until_disconnected()
    asyncio.run(client.close())
    
