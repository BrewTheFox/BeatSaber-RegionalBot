import discord
import time
import embed_poster
import aiohttp
import json
import re
import asyncio
import logging
from database import manager
from embeds import error, success
from load_config import get_string

plays = 0
p_data = {}
lp_data = {}
regex_scoresaber = re.compile("https://scoresaber\\.com/u/([0-9]*)")
regex_beatleader = re.compile("https://beatleader\\.xyz/u/([0-9]*)")


async def check_local_player_data(client: discord.Client):
    global lp_data
    current_lp_data = dict(lp_data)
    for player_key in current_lp_data.keys():
        if (
            current_lp_data[player_key]["timesregistered"] == 1
            and current_lp_data[player_key]["time"] < time.time()
        ):
            logging.info(f"Only playing in one platform: {player_key}")
            try:
                del lp_data[player_key]
            except NameError:
                continue
            asyncio.create_task(
                embed_poster.post_embeds(
                    datos=current_lp_data[player_key]["gameplayinfo"],
                    client=client,
                    gamestill=plays,
                )
            )
            reset_plays()
        elif current_lp_data[player_key]["time"] > time.time():
            continue
        else:
            logging.info("Se esta jugando doble")
            try:
                del lp_data[player_key]
            except NameError:
                continue
            asyncio.create_task(
                embed_poster.post_embeds(
                    datos=current_lp_data[player_key]["gameplayinfo"],
                    client=client,
                    gamestill=plays,
                )
            )
            reset_plays()


def reset_plays() -> None:
    global plays
    plays = 0


def update_local_player_data(player_id: int, data: dict):
    global lp_data
    player_id = str(player_id)
    if not player_id in list(lp_data.keys()):
        lp_data[player_id] = {
            "time": time.time() + 6,
            "timesregistered": 1,
            "gameplayinfo": data,
        }
    else:
        if lp_data[player_id]["gameplayinfo"].get("Scoresaber") != data.get(
            "Scoresaber"
        ) or lp_data[player_id]["gameplayinfo"].get("Beatleader") != data.get(
            "Beatleader"
        ):
            lp_data[player_id]["timesregistered"] += 1
            lp_data[player_id]["gameplayinfo"].update(data)


async def plays_plus_one(
    player_id: int, leaderboard: str, client: discord.Client
) -> None:
    global plays
    global p_data
    player_id = str(player_id)
    copy_pdata = dict(p_data)
    if not player_id in list(p_data.keys()):
        p_data[player_id] = {"time": time.time(), "leaderboard": leaderboard}
    for p_reference in copy_pdata:
        if (
            copy_pdata[p_reference]["time"] + 6 < time.time()
            or copy_pdata[p_reference]["leaderboard"] is leaderboard
        ):
            plays += 1
            actividad = discord.Game(
                get_string("Status", "Status").replace("{{var}}", str(plays)), type=1
            )
            await client.change_presence(status=discord.Status.idle, activity=actividad)
            if p_reference in p_data.keys():
                del p_data[p_reference]
        else:
            plays += 1
            actividad = discord.Game(
                get_string("Status", "Status").replace("{{var}}", str(plays)), type=1
            )
            await client.change_presence(status=discord.Status.idle, activity=actividad)
            if p_reference in p_data.keys():
                del p_data[p_reference]


async def link(link: str, uid: int):
    session = aiohttp.ClientSession()
    player = manager.load_player_discord(str(uid))

    if player:
        embed = error(get_string("UserAlreadyLinkedAccount", "UserHandling"))
        return embed

    link = link.replace("www.", "")
    if not link:
        embed = error(title=get_string("InvalidURL", "UserHandling"))
        return embed

    if link.startswith("https://scoresaber.com/u/") or link.startswith(
        "https://beatleader.xyz/u/"
    ):
        if link.startswith("https://scoresaber.com/u/"):
            id = regex_scoresaber.findall(link)[0]
            url = f"https://scoresaber.com/api/player/{id}/full"
        if link.startswith("https://beatleader.xyz/u/"):
            id = regex_beatleader.findall(link)[0]
            url = f"https://api.beatleader.com/player/{id}?stats=false&keepOriginalId=false"

        async with session as ses:
            async with ses.get(url) as request:
                response = await request.text()
                status = request.status

        if not '"errorMessage"' in response or status == 404:
            datos = json.loads(response)
            if manager.load_player_id(str(id)):
                embed = error(
                    get_string("AccountRegisteredByOtherUserTitle", "UserHandling")
                )
                embed.add_field(
                    name=get_string(
                        "AccountRegisteredByOtherUserTitleContent", "UserHandling"
                    ),
                    value=" ",
                )
                return embed
            else:
                embed = success(
                    get_string("WelcomeUser", "UserHandling").replace(
                        "{{name}}", datos["name"]
                    )
                )
                embed.add_field(
                    name=get_string("RegisteredCorrectly", "UserHandling"), value=" "
                )
                if link.startswith("https://beatleader.xyz/u/"):
                    embed.set_thumbnail(url=datos["avatar"])
                if link.startswith("https://scoresaber.com/u/"):
                    embed.set_thumbnail(url=datos["profilePicture"])
                manager.insert_player(id=str(id), discord=str(uid))
                return embed

        else:
            embed = discord.Embed(
                title=get_string("InvalidAccount", "UserHandling"),
                color=discord.Color.red(),
            )
            return embed
    else:
        embed = discord.Embed(
            title=get_string("ServiceUnavailable", "UserHandling"),
            color=discord.Color.red(),
        )
        return embed


async def unlink(uid: int):
    session = aiohttp.ClientSession()
    player = manager.load_player_discord(str(uid))
    if player:
        url = f"https://scoresaber.com/api/player/{player[0]}/full"
        async with session as ses:
            async with ses.get(url) as request:
                datos = json.loads(await request.text())
        embed = success(
            title=get_string("SuccessUnlink", "UserHandling").replace(
                "{{name}}", datos["name"]
            )
        )
        embed.set_thumbnail(url=datos["profilePicture"])
        manager.delete_player(uid)
    else:
        embed = error(get_string("NoAccountToUnlink", "UserHandling"))
    return embed
