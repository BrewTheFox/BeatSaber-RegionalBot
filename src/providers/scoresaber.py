import aiohttp
import discord
import json
import websockets
from core import player_handler
import asyncio
import logging
from database import manager
from core.embeds import player as player_embed
from core.embeds import error_with_fields
from core.load_config import get_string, get_configuration

COUNTRY = get_configuration()["Country"]


async def get_player_info(did: int) -> list:
    session = aiohttp.ClientSession()
    player = manager.load_player_discord(did)
    if player:
        async with session as ses:
            async with ses.get(
                f"https://scoresaber.com/api/player/{player[0]}/full"
            ) as request:
                data = json.loads(await request.text())
        embed = player_embed(discord.Color.yellow(), data)
        return embed, False
    embed = error_with_fields(
        get_string("AskUserToLink", "Misc"),
        [{"name": get_string("NoLinkedAccountUser", "Misc"), "value": " "}],
    )
    return embed, True


async def get_pass(player_id: str):
    async with aiohttp.ClientSession() as ses:
        async with ses.get(
            f"https://scoresaber.com/api/player/{player_id}/full"
        ) as request:
            player_info = json.loads(await request.text())

    manager.insert_top_player(
        0, player_id, player_info["pp"]
    )  # Take into account that 0 = ScoreSaber
    old_pp = manager.get_player_pp(0, player_id)
    players_passed = list(manager.get_players_between(0, old_pp[0], player_info["pp"]))
    try:
        if player_id == players_passed[-1][0]:
            players_passed.pop(-1)
        if len(players_passed) < 1 or players_passed == None:
            return [False, None, 0, 0, "0"]
        async with aiohttp.ClientSession() as ses:
            async with ses.get(
                f"https://api.beatleader.com/player/{players_passed[-1][0]}?keepOriginalId=false"
            ) as request:
                adversarial_info = json.loads(await request.text())
        manager.update_player_pp(1, player_id, player_info["pp"])
        return [
            True,
            adversarial_info["name"],
            adversarial_info["id"],
            abs(player_info["pp"] - adversarial_info["pp"]),
            str(player_info["countryRank"]),
        ]
    except:
        return [False, None, 0, 0, "0"]


async def receive(client: discord.Client):
    while True:
        try:
            async with websockets.connect("wss://scoresaber.com/ws") as socket:
                while True:
                    data = await socket.recv()
                    if data and "{" in data:
                        await player_handler.CheckLocalPlayerData(client)
                        data = json.loads(data)
                        if data.get("commandData"):
                            data["Scoresaber"] = True
                            if data["commandData"]["score"]["leaderboardPlayerInfo"][
                                "country"
                            ] == COUNTRY or manager.load_player_id(
                                str(
                                    data["commandData"]["score"][
                                        "leaderboardPlayerInfo"
                                    ]["id"]
                                )
                            ):
                                logging.info(
                                    f"Game by {data['commandData']['score']['leaderboardPlayerInfo']['name']} has been registered!"
                                )
                                playerid = data["commandData"]["score"][
                                    "leaderboardPlayerInfo"
                                ]["id"]
                                player_handler.update_local_player_data(playerid, data)
                            else:
                                asyncio.create_task(
                                    player_handler.plays_plus_one(
                                        data["commandData"]["score"][
                                            "leaderboardPlayerInfo"
                                        ]["id"],
                                        "scoresaber",
                                        client,
                                    )
                                )
        except Exception as e:
            logging.error(f"Disconnected from web scoresaber's socket. {e}")
