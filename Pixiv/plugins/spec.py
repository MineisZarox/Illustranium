import io
import os
import sys
import time
import asyncio
import traceback
import pprint as pr
from datetime import datetime
from telethon.errors import rpcbaseerrors
from telethon import events

from telethon.tl.tlobject import TLObject
from ..utilities.pasty import paste_message
from .. import pixiv, pxv, check_auth, Vars



def utc_to_local(utc_datetime):
    now_timestamp = time.time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(
        now_timestamp
    )
    return utc_datetime + offset

def yaml_format(obj, indent=0, max_str_len=256, max_byte_len=64):
    result = []
    if isinstance(obj, TLObject):
        obj = obj.to_dict()

    if isinstance(obj, dict):
        if not obj:
            return "dict:"
        items = obj.items()
        has_items = len(items) > 1
        has_multiple_items = len(items) > 2
        result.append(obj.get("_", "dict") + (":" if has_items else ""))
        if has_multiple_items:
            result.append("\n")
            indent += 2
        for k, v in items:
            if k == "_" or v is None:
                continue
            formatted = yaml_format(v, indent)
            if not formatted.strip():
                continue
            result.append(" " * (indent if has_multiple_items else 1))
            result.append(f"{k}:")
            if not formatted[0].isspace():
                result.append(" ")
            result.append(f"{formatted}")
            result.append("\n")
        if has_items:
            result.pop()
        if has_multiple_items:
            indent -= 2
    elif isinstance(obj, str):
        result = repr(obj[:max_str_len])
        if len(obj) > max_str_len:
            result += "…"
        return result
    elif isinstance(obj, bytes):
        if all(0x20 <= c < 0x7F for c in obj):
            return repr(obj)
        return "<…>" if len(obj) > max_byte_len else " ".join(f"{b:02X}" for b in obj)
    elif isinstance(obj, datetime):
        return utc_to_local(obj).strftime("%Y-%m-%d %H:%M:%S")
    elif hasattr(obj, "__iter__"):
        result.append("\n")
        indent += 2
        for x in obj:
            result.append(f"{' ' * indent}- {yaml_format(x, indent + 2)}")
            result.append("\n")
        result.pop()
        indent -= 2
    else:
        return repr(obj)
    return "".join(result)

async def aexec(code, smessatatus):
    message = event = smessatatus
    p = lambda _x: print(yaml_format(_x))
    reply = await event.get_reply_message()
    exec("async def __aexec(message, event , reply, client, p, chat): "
            + "".join(f"\n {l}" for l in code.split("\n")))

    return await locals()["__aexec"](
        message, event, reply, message.client, p, message.chat_id
    )

@pixiv.on(events.NewMessage(incoming=True, pattern="/pixi(?:\s|$)([\s\S]*)"))
@pixiv.on(events.MessageEdited(incoming=True, pattern="/pixi(?:\s|$)([\s\S]*)"))
@check_auth
async def evalution(event):
    cmd = "".join(event.message.message.split(maxsplit=1)[1:])
    if not cmd:
        return await event.reply("`Give something to run! ...`")
    eval_ = await event.reply("`Evalution in process ...`")
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None
    try:
        await aexec(cmd, event)
    except Exception:
        exc = traceback.format_exc()
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success"
    try:
        final_output = (f"**•  Eval : **\n```{cmd}``` \n\n**•  Output :**\n```{evaluation}``` \n")
        await eval_.edit(text=final_output)
    except:
        pastelink = await paste_message(evaluation, pastetype="s", markdown=False)
        final_output = (f"**•  Syntax : **\n```{cmd}``` \n\n**•  Output :**\n[here]({pastelink}) \n")
        await eval_.edit(text=final_output)


@pixiv.on(events.NewMessage(incoming=True, pattern="^/dels"))
@pixiv.on(events.MessageEdited(incoming=True, pattern="^/dels"))
@check_auth
async def delete_module(event):
    B = await event.get_reply_message()
    if B:
        msg_src = await event.get_reply_message()
        try:
            await msg_src.delete()
        except rpcbaseerrors.BadRequestError:
            pass
